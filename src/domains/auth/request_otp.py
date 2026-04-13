from random import choices
import string
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.lib.task.run_task import run_task
from src.lib.utils.lazycache import lazyload
from src.models.auth import RequestOTP
from src.models.response import DataResponse
from src.tasks.send_mail import send_mail_task


async def request_otp(payload: RequestOTP, db: Database, cache: Redis):
    user_collection = db.users
    user = await lazyload(cache, f'user:{payload.email}', loader=user_collection.find_one, params={'email': payload.email, 'hidden': False})
      
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'User not found: {payload.email}')

    code = ''.join(choices(string.digits, k=6))
    await cache.setex(f'OTP:{payload.email}', 300, code)

    run_task(
        send_mail_task,
        kwargs={
            'subject': 'Your OTP Code',
            'email': payload.email,
            'data': {'code': code},
            'template_file': 'otp_email.html'
        }
    )
    return DataResponse(message='OTP sent successfully')
