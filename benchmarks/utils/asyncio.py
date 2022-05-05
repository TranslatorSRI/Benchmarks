import asyncio
from typing import Coroutine, Sequence

async def gather(*coroutines: Sequence[Coroutine], limit: int = None):
    """
    Extension of asyncio.gather with a limit on the number of concurrent
    coroutines.

    Args:
        coroutines: Coroutines to run concurrently.
        limit: Limit on the number of coroutines to run concurrently.
    """
    if limit is None:
        return await asyncio.gather(*coroutines)

    semaphore = asyncio.Semaphore(limit)
    async def sem_coro(coroutine):
        async with semaphore:
            return await coroutine
    return await asyncio.gather(*(sem_coro(coro) for coro in coroutines))