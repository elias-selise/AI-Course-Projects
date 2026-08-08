import asyncio
import json
import logging
from typing import Optional
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from app.market.cache import PriceCache

logger = logging.getLogger("finally.api.stream")

router = APIRouter()


async def price_event_generator(request: Request, cache: PriceCache):
    last_version = -1
    while True:
        if await request.is_disconnected():
            break

        current_version = cache.version
        if current_version != last_version:
            last_version = current_version
            all_ticks = cache.get_all()
            payload = [tick.model_dump() for tick in all_ticks.values()]
            yield {
                "event": "price_update",
                "data": json.dumps(payload),
            }

        await asyncio.sleep(0.5)


@router.get("/api/stream/prices")
async def stream_prices(request: Request):
    cache: PriceCache = getattr(request.app.state, "price_cache", None)
    if cache is None:
        cache = PriceCache()
    return EventSourceResponse(price_event_generator(request, cache))


def create_stream_router(cache: PriceCache) -> APIRouter:
    r = APIRouter()

    @r.get("/api/stream/prices")
    async def stream_prices_with_cache(request: Request):
        return EventSourceResponse(price_event_generator(request, cache))

    return r
