from jwt import PyJWTError
import jwt
from fastapi import HTTPException, status
from pymongo.database import Database
from redis.asyncio import Redis

from src.domains.auth.model import CurrentUser
from src.lib.utils.lazycache import lazyload
from ...config import config


async def validate_token(token: str, db: Database, cache: Redis) -> CurrentUser:
    try:
        payload = jwt.decode(token, config.SECRET, algorithms=config.ALGORITHM)
        email = payload.get('sub')

        if email is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Token is invalid')

        user = await lazyload(cache, f'user:{email}', loader=db.users.find_one, params={'filter': {'email': email, 'hidden': False}})
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'User not found')

        return CurrentUser(id=str(user.get('_id')), email=email)
    except PyJWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Token is invalid')
