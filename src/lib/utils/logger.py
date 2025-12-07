import logging
import sys
import os
from logging.handlers import RotatingFileHandler
import contextvars

from src.config import config

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] [%(request_id)s] - [%(message)s]"
DATE_FORMAT = "%Y-%m-%d %H:%M%:%S"

LOG_DIR = os.path.join(os.path.dirname(__file__), '../../logs')
LOG_DIR = os.path.abspath(LOG_DIR)
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
ENV = config.ENV

os.makedirs(LOG_DIR, exist_ok=True)

_request_id_ctx = contextvars.ContextVar('request_id', default='-')


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = _request_id_ctx.get('-')
        return True


def get_logger(name: str = 'app'):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.addFilter(RequestIdFilter())
        console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
        logger.addHandler(console_handler)

        if ENV != 'test':
            file_handler = RotatingFileHandler(
                LOG_FILE, maxBytes=5*1024*1024, backupCount=5
            )
            file_handler.addFilter(RequestIdFilter())
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
            logger.addHandler(file_handler)

    return logger


def set_request_id(request_id: str):
    _request_id_ctx.set(request_id)


def clear_request_id():
    _request_id_ctx.set('-')