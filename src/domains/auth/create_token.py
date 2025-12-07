import jwt
from datetime import datetime, timedelta

from ...config import config
from .model import TokenData

def create_token(data: TokenData, life_span: int = config.CACHE_TTL):
    to_encode = data.model_dump()
    expire = datetime.now() + timedelta(seconds=life_span)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, config.SECRET, algorithm=config.ALGORITHM)
