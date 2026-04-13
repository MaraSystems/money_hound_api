from pymongo.database import Database
from fastapi import HTTPException, status
from redis.asyncio import Redis

from src.lib.task.run_task import run_task
from src.lib.utils.config import APP_NAME
from src.lib.utils.lazycache import lazyload

from src.models.auth import CreateUser
from src.models.user import User
from src.models.response import DataResponse
from src.tasks.send_mail import send_mail_task


async def register_user(payload: CreateUser, db: Database, cache: Redis):
    user_collection = db.users
    existing = await lazyload(cache, f'user:{payload.email}', loader=user_collection.find_one, params={'email': payload.email, 'hidden': False})

    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'Email not available: {payload.email}')
    
    insert = await user_collection.insert_one(payload.model_dump())
    user = await user_collection.find_one({'_id': insert.inserted_id})

    mail_data = {'user_name': user.get('firstname'), 'verification_link': '#'}
    run_task(
        send_mail_task,
        kwargs={
            'subject': f'Welcome to {APP_NAME}',
            'email': user.get('email'),
            'data': mail_data,
            'template_file': 'welcome_email.html'
        }
    )
    return DataResponse(data=User(**user), message=f'Registration successful: {payload.email}')
