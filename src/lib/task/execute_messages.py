import asyncio

from src.lib.task.message_queue import msg_queue
from src.tasks.run_simulation import run_simulation_task
from src.tasks.send_mail import send_mail_task
from src.tasks.sync_knowledge import sync_knowledge_task


async def execute_messages():
    await msg_queue.connect()
    asyncio.create_task(
        msg_queue.consume(run_simulation_task.__name__, run_simulation_task)
    )

    asyncio.create_task(
        msg_queue.consume(send_mail_task.__name__, send_mail_task)
    )

    asyncio.create_task(
        msg_queue.consume(sync_knowledge_task.__name__, sync_knowledge_task)
    )
