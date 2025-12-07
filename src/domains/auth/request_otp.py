from random import choices
import string
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.lib.utils.lazycache import lazyload

from ...domains.auth.model import RequestOTP
from ...lib.utils.response import DataResponse
from ...tasks.mailer import send_mail


async def request_otp(payload: RequestOTP, db: Database, cache: Redis):
    user_collection = db.users
    user = await lazyload(cache, f'user:{payload.email}', loader=user_collection.find_one, params={'email': payload.email, 'hidden': False})
      
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f'User not found: {payload.email}')

    code = ''.join(choices(string.digits, k=6))
    await cache.setex(f'OTP:{payload.email}', 300, code)

    send_mail.delay('Your OTP Code', payload.email, {'code': code}, 'otp_email.html')
    return DataResponse(message='OTP sent successfully')
