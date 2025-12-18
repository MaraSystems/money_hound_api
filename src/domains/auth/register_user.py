from pymongo.database import Database
from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.config.config import APP_NAME
from src.lib.utils.lazycache import lazyload

from .model import CreateUser
from ..users.model import User
from ...lib.utils.response import DataResponse
from ...tasks.mailer import send_mail


async def register_user(payload: CreateUser, db: Database, cache: Redis):
    user_collection = db.users
    existing = await lazyload(cache, f'user:{payload.email}', loader=user_collection.find_one, params={'filter': {'email': payload.email, 'hidden': False}})

    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Email not available: {payload.email}')
    
    insert = await user_collection.insert_one(payload.model_dump())
    user = await user_collection.find_one({'_id': insert.inserted_id})

    mail_data = {'user_name': user.get('firstname'), 'verification_link': '#'}
    send_mail.delay(f'Welcome to {APP_NAME}', user.get('email'), mail_data, 'welcome_email.html')
    return DataResponse(data=User(**user), message=f'Registration successful: {payload.email}')
