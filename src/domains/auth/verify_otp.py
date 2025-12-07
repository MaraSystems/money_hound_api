from fastapi import HTTPException, status
from redis.asyncio import Redis

from ...domains.auth.create_token import create_token
from ...domains.auth.model import Token, TokenData, VerifyOTP
from ...lib.utils.response import DataResponse


async def verify_otp(payload: VerifyOTP, cache: Redis):
    key = f'OTP:{payload.email}'
    code = await cache.get(key)
    
    if not code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'OTP has expired')
    
    if code != payload.code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, 'OTP is invalid')

    token = create_token(TokenData(sub=payload.email))
    await cache.delete(key)

    return DataResponse(data=Token(token=token, access='Bearer'))
