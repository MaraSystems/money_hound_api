from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse

from ..lib.utils.logger import get_logger

http_error_logger = get_logger('HTTPException')
def http_exception_handler(request: Request, exc: HTTPException):
    http_error_logger.warning(f'⚠️ Error on {request.url}: {exc}')
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': 'HTTP Error',
            'message': exc.detail
        }
    )

validation_error_logger = get_logger('RequestValidationError')
def validation_exception_handler(request: Request, exc: RequestValidationError):
    validation_error_logger.error(f'⛔️ Error on {request.url}: {exc}')
    error: dict = exc.errors()[0]

    message = f"\'{error['loc'][1]}\': {error['msg']}" 
        

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            'success': False,
            'error': 'Validation Error',
            'message': message
        }
    )

response_error_logger = get_logger('ResponseValidationException')
def response_exception_handler(request: Request, exc: ResponseValidationError):
    response_error_logger.error(f'⛔️ Error on {request.url}: {exc}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'success': False,
            'error': 'Response Error',
            'message': str(exc)
        }
    )


system_error_logger = get_logger('SystemException')
def system_exception_handler(request: RequestValidationError, exc: Exception):
    http_error_logger.critical(f'🔥 Unexpected error on {request.url}: {exc}')
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'success': False,
            'error': 'Internal Server Error',
            'message': str(exc)
        }
    )