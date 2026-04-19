"""WebSocket endpoint for real-time generation progress."""
import asyncio
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import redis.asyncio as aioredis

from app.config import settings

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/generation/{task_id}")
async def generation_progress_ws(websocket: WebSocket, task_id: str):
    """
    WebSocket endpoint that subscribes to Redis Pub/Sub
    for real-time generation progress updates.
    """
    await websocket.accept()

    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_client.pubsub()

    try:
        # Subscribe to task-specific channel
        channel = f"task_progress:{task_id}"
        await pubsub.subscribe(channel)

        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": "Subscribed to generation progress",
        })

        # Listen for messages
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=1.0
            )
            if message and message["type"] == "message":
                data = json.loads(message["data"])
                await websocket.send_json(data)

                # If generation is complete or errored, close connection
                if data.get("status") in ("completed", "error"):
                    await websocket.send_json({
                        "type": "done",
                        "status": data.get("status"),
                    })
                    break

            # Heartbeat to keep connection alive
            try:
                await asyncio.wait_for(
                    websocket.receive_text(), timeout=0.1
                )
            except asyncio.TimeoutError:
                pass

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await redis_client.close()
