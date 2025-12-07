from fastapi import APIRouter, Depends, Query, Request
from typing import Annotated
from bson import ObjectId

from src.config.cache import get_cache
from src.domains.auth.get_profile import get_profile
from .register_user import register_user
from .request_otp import request_otp
from .verify_otp import verify_otp
from .update_profile import update_profile
from .delete_profile import delete_profile
from ...domains.users.model import User
from ...middlewares.auth_guard import get_current_user
from .model import CreateUser, RequestOTP, VerifyOTP, Token, UpdateProfile
from ...config.database import get_db
from ...lib.utils.response import DataResponse
from ...config.config import REQUEST_LIMIT
from ...middlewares.limits import rate_limit


auth_router = APIRouter(prefix='/auth')


@auth_router.post('/register', response_model=DataResponse[User], name="CreateUser User", status_code=201)
@rate_limit.limit(f'{REQUEST_LIMIT}/hour')
async def register(request: Request, payload: CreateUser, db=Depends(get_db), cache=Depends(get_cache)):
    return await register_user(payload, db, cache)


@auth_router.get('/request', response_model=DataResponse[None], name="Request OTP")
async def request(payload: Annotated[Query, Depends(RequestOTP)], db=Depends(get_db), cache=Depends(get_cache)):
    return await request_otp(payload, db, cache)


@auth_router.post('/verify', response_model=DataResponse[Token], status_code=201, name="Verify OTP")
async def verify(payload: VerifyOTP, cache=Depends(get_cache)):
    return await verify_otp(payload, cache)


@auth_router.get('/profile', response_model=DataResponse[User], name="Get User Profile")
async def profile(user=Depends(get_current_user), db=Depends(get_db), cache=Depends(get_cache)):
    return await get_profile(ObjectId(user.id), db, cache)


@auth_router.patch('/profile', response_model=DataResponse[User], name="Update User Profile")
async def update(payload: UpdateProfile, user=Depends(get_current_user), db=Depends(get_db), cache=Depends(get_cache)):
    user_id = ObjectId(user.id)
    return await update_profile(user_id, payload, db, cache)


@auth_router.delete('/profile', response_model=DataResponse[None], name="Delete User Profile")
async def delete(user=Depends(get_current_user), db=Depends(get_db), cache=Depends(get_cache)):
    user_id = ObjectId(user.id)
    return await delete_profile(user_id, db, cache)