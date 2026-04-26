from src.lib.task.message_queue import msg_queue
from src.lib.utils.config import ENV, ENVIRONMENTS, EXTERNAL_BACKGROUND, RABBIT_URL
from src.lib.utils.logger import get_logger
from src.lib.task.task_manager import task_manager

logger = get_logger('TaskRunner')


async def publish_message(task: callable, payload: dict = {}):
    """Execute a background task using TaskManager or Celery based on configuration.

    In testing environment, tasks are skipped. When EXTERNAL_BACKGROUND is disabled,
    tasks run in the local TaskManager. Otherwise, tasks are dispatched to Celery.

    Args:
        task: Callable task function to execute
        payload: Arguments to pass to the task

    Returns:
        Celery task result if using Celery, None otherwise
    """
    if ENV == ENVIRONMENTS.TESTING:
        return

    if not EXTERNAL_BACKGROUND:
        logger.info(f'Running task {task.__name__} in TaskManager')
        task_manager.add_task(task, payload)
        return

    logger.info(f'Running task {task.__name__} in MessageQueue')
    await msg_queue.connect()
    await msg_queue.publish(task.__name__, payload)
    return


