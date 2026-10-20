"""SSE stream endpoint (auth in Phase 03)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import redis.asyncio as redis
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/api/v1/realtime", tags=["realtime"])


async def _redis_subscriber(client: redis.Redis, channel: str) -> AsyncIterator[bytes]:
    pubsub = client.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("type") == "message":
                data = message["data"]
                if isinstance(data, bytes):
                    data = data.decode()
                yield f"data: {data}\n\n".encode()
            await asyncio.sleep(0.05)
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()


def build_sse_router(get_redis: object) -> APIRouter:
    @router.get("/stream")
    async def stream(request: Request) -> StreamingResponse:
        client = get_redis()  # type: ignore[operator]
        channel = request.query_params.get("channel", "platform:events")
        return StreamingResponse(
            _redis_subscriber(client, channel),
            media_type="text/event-stream",
        )

    return router
