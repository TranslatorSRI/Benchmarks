import asyncio
from typing import Coroutine, Optional, Sequence


async def gather(*coroutines: Sequence[Coroutine], limit: Optional[int] = None):
    """
    Extension of asyncio.gather with a limit on the number of concurrent
    coroutines.

    Args:
        coroutines: (list of coroutines) Coroutines to run concurrently.
        limit: (int, optional) Limit on the number of coroutines to run
            concurrently.
    """
    if limit is None:
        return await asyncio.gather(*coroutines)

    semaphore = asyncio.Semaphore(limit)
    async def sem_coro(coroutine):
        async with semaphore:
            return await coroutine
    return await asyncio.gather(*(sem_coro(coro) for coro in coroutines))