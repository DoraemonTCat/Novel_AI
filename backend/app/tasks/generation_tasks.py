"""Novel generation Celery tasks."""
import json
import logging

import redis
from celery import current_task

from app.config import settings
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

# Synchronous Redis client for Celery workers
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)


def publish_progress(task_id: str, data: dict):
    """Publish generation progress to Redis Pub/Sub."""
    channel = f"task_progress:{task_id}"
    redis_client.publish(channel, json.dumps(data))


@celery_app.task(bind=True, name="generate_novel")
def generate_novel_task(self, novel_id: str):
    """
    Main novel generation task.
    Generates outline then creates chapters one by one.
    Publishes progress to Redis Pub/Sub for WebSocket consumption.
    """
    import asyncio
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session, sessionmaker

    # Use sync DB connection for Celery worker
    sync_db_url = settings.DATABASE_URL.replace("+asyncpg", "+psycopg2")
    engine = create_engine(sync_db_url)
    SessionLocal = sessionmaker(bind=engine)

    task_id = self.request.id

    try:
        with SessionLocal() as db:
            from app.models.novel import Novel
            from app.models.chapter import Chapter

            novel = db.query(Novel).filter(Novel.id == novel_id).first()
            if not novel:
                raise ValueError(f"Novel {novel_id} not found")

            total_chapters = novel.total_chapters

            # Publish: Starting
            publish_progress(task_id, {
                "type": "progress",
                "status": "outline",
                "novel_id": novel_id,
                "task_id": task_id,
                "current_chapter": 0,
                "total_chapters": total_chapters,
                "progress_percent": 0,
                "message": "Generating story outline...",
            })

            # Step 1: Generate outline using AI
            ai_provider = _get_ai_provider(novel.ai_provider, novel.ai_model)
            outline = ai_provider.generate_outline(
                prompt=novel.prompt,
                genre=novel.genre,
                language=novel.language,
                num_chapters=total_chapters,
                writing_style=novel.writing_style,
                tone=novel.tone,
                pov=novel.pov,
            )

            novel.outline = outline
            db.commit()

            publish_progress(task_id, {
                "type": "progress",
                "status": "generating",
                "novel_id": novel_id,
                "task_id": task_id,
                "current_chapter": 0,
                "total_chapters": total_chapters,
                "progress_percent": 5,
                "message": "Outline generated! Starting chapters...",
            })

            # Step 2: Generate each chapter
            previous_summaries = []

            for chapter_num in range(1, total_chapters + 1):
                # Check if task was revoked
                from celery.result import AsyncResult
                if AsyncResult(task_id).state == 'REVOKED':
                    novel.status = "paused"
                    db.commit()
                    return {"status": "cancelled"}

                chapter_outline = outline.get("chapters", [{}])[chapter_num - 1] if outline.get("chapters") else {}

                publish_progress(task_id, {
                    "type": "progress",
                    "status": "generating",
                    "novel_id": novel_id,
                    "task_id": task_id,
                    "current_chapter": chapter_num,
                    "total_chapters": total_chapters,
                    "progress_percent": 5 + (chapter_num - 1) / total_chapters * 90,
                    "current_chapter_title": chapter_outline.get("title", f"Chapter {chapter_num}"),
                    "message": f"Writing chapter {chapter_num}/{total_chapters}...",
                })

                # Generate chapter content
                content = ai_provider.generate_chapter(
                    outline=outline,
                    chapter_num=chapter_num,
                    chapter_outline=chapter_outline,
                    previous_summaries=previous_summaries,
                    language=novel.language,
                    writing_style=novel.writing_style,
                    tone=novel.tone,
                    pov=novel.pov,
                    target_length=novel.chapter_length_target,
                )

                # Calculate word count
                word_count = len(content.split())

                # Create chapter record
                chapter = Chapter(
                    novel_id=novel_id,
                    chapter_number=chapter_num,
                    title=chapter_outline.get("title", f"Chapter {chapter_num}"),
                    content=content,
                    word_count=word_count,
                    status="completed",
                )
                db.add(chapter)
                db.commit()

                # Generate summary for context
                summary = ai_provider.summarize_chapter(content, novel.language)
                previous_summaries.append({
                    "chapter": chapter_num,
                    "title": chapter.title,
                    "summary": summary,
                })

                publish_progress(task_id, {
                    "type": "progress",
                    "status": "generating",
                    "novel_id": novel_id,
                    "task_id": task_id,
                    "current_chapter": chapter_num,
                    "total_chapters": total_chapters,
                    "progress_percent": 5 + chapter_num / total_chapters * 90,
                    "preview_text": content[:200] + "...",
                    "message": f"Chapter {chapter_num} completed! ({word_count} words)",
                })

            # Step 3: Mark novel as complete
            novel.status = "completed"
            db.commit()

            publish_progress(task_id, {
                "type": "progress",
                "status": "completed",
                "novel_id": novel_id,
                "task_id": task_id,
                "current_chapter": total_chapters,
                "total_chapters": total_chapters,
                "progress_percent": 100,
                "message": "Novel generation complete!",
            })

            return {"status": "completed", "novel_id": novel_id}

    except Exception as e:
        logger.error(f"Generation failed for novel {novel_id}: {e}")

        publish_progress(task_id, {
            "type": "progress",
            "status": "error",
            "novel_id": novel_id,
            "task_id": task_id,
            "error_message": str(e),
            "message": f"Generation failed: {str(e)}",
        })

        # Update novel status
        try:
            with SessionLocal() as db:
                from app.models.novel import Novel
                novel = db.query(Novel).filter(Novel.id == novel_id).first()
                if novel:
                    novel.status = "error"
                    db.commit()
        except Exception:
            pass

        raise


def _get_ai_provider(provider_name: str, model_name: str):
    """Factory to get the appropriate AI provider."""
    from app.services.ai_providers import get_provider
    return get_provider(provider_name, model_name)
