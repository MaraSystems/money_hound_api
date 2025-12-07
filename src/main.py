from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.openapi.utils import get_openapi
from pydantic import ValidationError

from .middlewares.error_handler import http_exception_handler, response_exception_handler, system_exception_handler, validation_exception_handler
from .middlewares.requests_logger import RequestLoggingMiddleware
from .lib.utils.response import DataResponse
from .router import register_routes
from .config import config
from .lib.utils.logger import get_logger

logger = get_logger('app')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('🚀 Application starting...')

    yield
    logger.info("👋 Application shutting down...")


app = FastAPI(title=config.APP_NAME, lifespan=lifespan)

register_routes(app)

app.add_middleware(RequestLoggingMiddleware)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ResponseValidationError, response_exception_handler)
app.add_exception_handler(Exception, system_exception_handler)


@app.get('/', tags=["Root"], response_model=DataResponse[None])
def home():
    return DataResponse(message='😊 Hey you.')


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Fast_API API",
        version="1.0.0",
        description="API documentation with JWT Bearer authentication",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
