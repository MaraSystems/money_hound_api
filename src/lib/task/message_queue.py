import json
from logging import Logger
from typing import Optional
import aio_pika
from aio_pika import Connection, Channel, DeliveryMode, Message

from src.lib.utils.config import RABBIT_URL
from src.lib.utils.logger import get_logger

class MessageQueue:
    def __init__(self, url: str) -> None:
        self.url = url
        self._connection: Optional[Connection] = None
        self._channel: Optional[Channel] = None
        self.logger = get_logger('MessageQueue Logger')

    @property
    def channel(self) -> Channel:
        if not self._channel:
            raise RuntimeError("MessageQueue not connected. Call connect first.")
        return self._channel
    
    async def connect(self):
        self._connection = await aio_pika.connect_robust(self.url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)

    async def disconnect(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    async def publish(self, name: str, payload: dict):
        await self.channel.declare_queue(name, durable=True)
        message = Message(
            body=json.dumps(payload).encode(),
            content_type="applicaiton/json",
            delivery_mode=DeliveryMode.PERSISTENT
        )

        await self.channel.default_exchange.publish(
            message=message,
            routing_key=name
        )

    async def consume(self, name: str, handler):
        queue = await self.channel.declare_queue(name, durable=True)
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process(requeue=True):
                    try:
                        payload = json.loads(message.body.decode())
                        await handler(payload)
                    except Exception as e:
                        self.logger.error(f"Error processing message: {e}")
                        await message.nack(requeue=True)


msg_queue = MessageQueue(RABBIT_URL)