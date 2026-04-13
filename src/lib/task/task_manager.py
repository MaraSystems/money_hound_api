import asyncio
from dataclasses import dataclass


@dataclass
class Task:
    """Represents a managed background task.

    Attributes:
        name: Name of the task function
        coro: The coroutine or executor task
        kwargs: Arguments passed to the task
    """

    name: str
    coro: asyncio.Task
    kwargs: dict


class TaskManager:
    """Manages and orchestrates background tasks.

    Handles both async coroutines and synchronous functions by running
    them in an event loop or executor respectively.
    """

    def __init__(self):
        """Initialize the task manager with an empty task list."""
        self.tasks = []

    def add_task(self, func: callable, **kwargs) -> asyncio.Task:
        """Add a task to the manager and start it immediately.

        Args:
            func: Callable function to execute (async or sync)
            **kwargs: Arguments to pass to the function

        Returns:
            The created asyncio.Task instance
        """
        if asyncio.iscoroutinefunction(func):
            task = asyncio.create_task(func(**kwargs))
        else:
            loop = asyncio.get_event_loop()
            task = loop.run_in_executor(None, lambda: func(**kwargs))

        self.tasks.append(Task(name=func.__name__, coro=func, kwargs=kwargs))
        return task

    async def wait_all(self):
        """Wait for all tasks in the manager to complete."""
        await asyncio.gather(*[task.coro for task in self.tasks])


task_manager = TaskManager()
