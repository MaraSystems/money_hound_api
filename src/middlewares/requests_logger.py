import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import uuid

from ..lib.utils.logger import get_logger, set_request_id, clear_request_id

logger = get_logger('requests')

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        set_request_id(request_id)

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(f'{request.client.host} - {request.method} {request.url.path} -> {response.status_code} [{duration:.2f}s]')

        response.headers['X-Request-ID'] = request_id
        clear_request_id()

        return response