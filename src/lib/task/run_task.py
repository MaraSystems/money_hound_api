from src.lib.utils.config import ENV, ENVIRONMENTS, EXTERNAL_BACKGROUND
from src.lib.utils.logger import get_logger
from src.lib.task.task_manager import task_manager
from src.tasks.queue import celery_app

logger = get_logger('TaskRunner')


def run_task(task: callable, kwargs: dict = {}):
    """Execute a background task using TaskManager or Celery based on configuration.

    In testing environment, tasks are skipped. When EXTERNAL_BACKGROUND is disabled,
    tasks run in the local TaskManager. Otherwise, tasks are dispatched to Celery.

    Args:
        task: Callable task function to execute
        kwargs: Arguments to pass to the task

    Returns:
        Celery task result if using Celery, None otherwise
    """
    if ENV == ENVIRONMENTS.TESTING:
        return None

    if not EXTERNAL_BACKGROUND:
        logger.info(f'Running task {task.__name__} in TaskManager')
        task_manager.add_task(task, **kwargs)
        return None

    logger.info(f'Running task {task.__name__} in celery')
    return celery_app.send_task(task.__name__, kwargs=kwargs)
