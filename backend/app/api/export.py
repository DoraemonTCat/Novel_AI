"""Export API — Generate PDF, EPUB, Markdown, TXT files from novels."""
import io
import os
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.chapter import Chapter
from app.models.novel import Novel
from app.models.user import User
from app.schemas.export import ExportRequest

router = APIRouter(prefix="/api/export", tags=["Export"])


@router.post("/")
@limiter.limit("10/minute")
async def export_novel(
    request: Request,
    export_req: ExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export a novel in the requested format."""
    # Verify ownership
    result = await db.execute(
        select(Novel).where(
            Novel.id == export_req.novel_id,
            Novel.user_id == current_user.id,
        )
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    # Get chapters
    query = select(Chapter).where(
        Chapter.novel_id == export_req.novel_id,
        Chapter.status == "completed",
    ).order_by(Chapter.chapter_number)

    if export_req.chapters:
        query = query.where(Chapter.chapter_number.in_(export_req.chapters))

    result = await db.execute(query)
    chapters = result.scalars().all()

    if not chapters:
        raise HTTPException(status_code=400, detail="No completed chapters to export")

    # Route to appropriate exporter
    if export_req.format == "txt":
        return _export_txt(novel, chapters)
    elif export_req.format == "markdown":
        return _export_markdown(novel, chapters)
    elif export_req.format == "pdf":
        return await _export_pdf(novel, chapters)
    elif export_req.format == "epub":
        return _export_epub(novel, chapters)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {export_req.format}")


def _export_txt(novel, chapters):
    """Export as plain text."""
    content = f"{novel.title}\n{'=' * len(novel.title)}\n\n"
    if novel.description:
        content += f"{novel.description}\n\n{'—' * 40}\n\n"

    for ch in chapters:
        title = ch.title or f"ตอนที่ {ch.chapter_number}"
        content += f"\n{'—' * 40}\n"
        content += f"ตอนที่ {ch.chapter_number}: {title}\n"
        content += f"{'—' * 40}\n\n"
        content += f"{ch.content}\n\n"

    buffer = io.BytesIO(content.encode("utf-8"))
    filename = f"{novel.title}.txt"
    return StreamingResponse(
        buffer,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _export_markdown(novel, chapters):
    """Export as Markdown."""
    content = f"# {novel.title}\n\n"
    if novel.description:
        content += f"> {novel.description}\n\n---\n\n"

    for ch in chapters:
        title = ch.title or f"ตอนที่ {ch.chapter_number}"
        content += f"## ตอนที่ {ch.chapter_number}: {title}\n\n"
        content += f"{ch.content}\n\n---\n\n"

    buffer = io.BytesIO(content.encode("utf-8"))
    filename = f"{novel.title}.md"
    return StreamingResponse(
        buffer,
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


async def _export_pdf(novel, chapters):
    """Export as PDF using WeasyPrint (supports Thai fonts)."""
    try:
        from weasyprint import HTML

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A5; margin: 2cm; }}
                body {{
                    font-family: 'Noto Sans Thai', 'TH Sarabun New', sans-serif;
                    font-size: 14px;
                    line-height: 1.8;
                    color: #1a1a1a;
                }}
                h1 {{
                    text-align: center;
                    font-size: 24px;
                    margin-bottom: 30px;
                    color: #2d2d2d;
                }}
                h2 {{
                    font-size: 18px;
                    margin-top: 40px;
                    margin-bottom: 20px;
                    color: #4a4a4a;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 8px;
                }}
                .chapter-content {{
                    text-indent: 2em;
                    text-align: justify;
                }}
                .separator {{
                    text-align: center;
                    margin: 30px 0;
                    color: #aaa;
                }}
                p {{ margin-bottom: 0.8em; }}
            </style>
        </head>
        <body>
            <h1>{novel.title}</h1>
        """

        if novel.description:
            html_content += f'<p style="text-align: center; color: #666; font-style: italic;">{novel.description}</p>'
            html_content += '<div class="separator">⸻</div>'

        for ch in chapters:
            title = ch.title or f"ตอนที่ {ch.chapter_number}"
            html_content += f'<h2>ตอนที่ {ch.chapter_number}: {title}</h2>'
            # Convert newlines to paragraphs
            paragraphs = ch.content.split("\n\n")
            for p in paragraphs:
                p = p.strip()
                if p:
                    html_content += f'<p class="chapter-content">{p}</p>'

        html_content += "</body></html>"

        pdf_bytes = HTML(string=html_content).write_pdf()
        buffer = io.BytesIO(pdf_bytes)
        filename = f"{novel.title}.pdf"

        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )


def _export_epub(novel, chapters):
    """Export as EPUB ebook."""
    try:
        from ebooklib import epub

        book = epub.EpubBook()
        book.set_identifier(str(novel.id))
        book.set_title(novel.title)
        book.set_language(novel.language if novel.language != "mixed" else "th")
        book.add_author("Novel AI")

        # CSS for epub
        style = epub.EpubItem(
            uid="style",
            file_name="style/default.css",
            media_type="text/css",
            content=b"""
                body { font-family: serif; line-height: 1.8; }
                h1 { text-align: center; margin-bottom: 2em; }
                h2 { margin-top: 2em; }
                p { text-indent: 2em; margin-bottom: 0.5em; }
            """,
        )
        book.add_item(style)

        epub_chapters = []
        for ch in chapters:
            title = ch.title or f"ตอนที่ {ch.chapter_number}"
            epub_ch = epub.EpubHtml(
                title=title,
                file_name=f"chapter_{ch.chapter_number}.xhtml",
                lang=novel.language if novel.language != "mixed" else "th",
            )

            paragraphs = ch.content.split("\n\n")
            html = f"<h2>{title}</h2>"
            for p in paragraphs:
                p = p.strip()
                if p:
                    html += f"<p>{p}</p>"

            epub_ch.content = html.encode("utf-8")
            epub_ch.add_item(style)
            book.add_item(epub_ch)
            epub_chapters.append(epub_ch)

        # Table of contents
        book.toc = epub_chapters
        book.spine = ["nav"] + epub_chapters

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Write to buffer
        buffer = io.BytesIO()
        epub.write_epub(buffer, book, {})
        buffer.seek(0)

        filename = f"{novel.title}.epub"
        return StreamingResponse(
            buffer,
            media_type="application/epub+zip",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"EPUB generation failed: {str(e)}"
        )
