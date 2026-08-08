import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from .cache import PriceCache


def create_stream_router(cache: PriceCache) -> APIRouter:
    router = APIRouter(prefix="/api/stream", tags=["stream"])

    async def _generate_events(request: Request) -> AsyncGenerator[str, None]:
        last_version = -1
        ping_counter = 0

        while True:
            if await request.is_disconnected():
                break

            current_version = cache.version
            if current_version != last_version:
                last_version = current_version
                all_prices = cache.get_all()
                data = [update.to_dict() for update in all_prices.values()]
                yield f"event: price_update\ndata: {json.dumps(data)}\n\n"
                ping_counter = 0
            else:
                ping_counter += 1
                if ping_counter >= 30:  # ~15 seconds heartbeat (30 * 0.5s)
                    yield f"event: ping\ndata: {json.dumps({'type': 'ping'})}\n\n"
                    ping_counter = 0

            await asyncio.sleep(0.5)

    @router.get("/prices")
    async def stream_prices(request: Request):
        return StreamingResponse(
            _generate_events(request),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return router
