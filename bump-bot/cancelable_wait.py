import asyncio


class CancelableWait:
    wait_task: asyncio.Task | None = None
    wait_task_lock = asyncio.Lock()
    length: float

    def __init__(self, l: float) -> None:
        self.length = l

    async def wait(self) -> bool:
        async with self.wait_task_lock:
            if self.wait_task:
                self.wait_task.cancel()
            self.wait_task = asyncio.create_task(asyncio.sleep(self.length))
        try:
            await self.wait_task
        except asyncio.CancelledError:
            return False
        self.wait_task = None
        return True
