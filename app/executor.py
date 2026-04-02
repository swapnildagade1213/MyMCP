import inspect
import anyio
from typing import Callable, Dict, Any


class AsyncToolExecutor:
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register(self, name: str, handler: Callable):
        self._handlers[name] = handler

    async def execute(self, name: str, payload: dict) -> Any:
        if name not in self._handlers:
            raise ValueError(f"Handler '{name}' not registered")

        handler = self._handlers[name]

        # ✅ async handler
        if inspect.iscoroutinefunction(handler):
            return await handler(**payload)

        # ✅ sync handler → run safely in worker thread
        return await anyio.to_thread.run_sync(
            lambda: handler(**payload)
        )
