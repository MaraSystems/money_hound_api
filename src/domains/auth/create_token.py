import jwt
from datetime import datetime, timedelta

from src.models.auth import TokenData
from src.lib.utils import config

def create_token(data: TokenData, life_span: int = config.CACHE_TTL):
    to_encode = data.model_dump()
    expire = datetime.now() + timedelta(seconds=life_span)
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, config.SECRET, algorithm=config.ALGORITHM)
