from fastapi import Depends, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.requests import Request

from src.config.cache import get_cache

from ..config.database import get_db
from ..domains.auth.validate_token import validate_token



async def get_current_user(request: Request, db=Depends(get_db), cache=Depends(get_cache)):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    bearer, token = auth_header.split(' ')
    if bearer.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Authorization header")
    
    try:
        user = await validate_token(token, db, cache)
        request.state.user = user
    except HTTPException as e:
        raise e

    return request.state.user