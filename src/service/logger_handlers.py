import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from src.configs.settings import settings

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',  # Белый
        'INFO': '\033[92m',  # Зеленый
        'WARNING': '\033[93m',  # Желтый
        'ERROR': '\033[91m',  # Красный
    }

    def format(self, record):
        color = self.COLORS.get(record.levelname, '')
        message = super().format(record)
        return f'{color}{message}\033[0m'  # \033[0m - сброс цвета


class JsonFormatter(logging.Formatter):
    def format(self, record):
        json_record = {
            "timestamp": f"{datetime.utcnow().isoformat(sep='T', timespec='milliseconds')}Z",
            "service.name": settings.TITLE,
            "log.level": getattr(record, "levelname", None),
            "message": getattr(record, "msg", None)
        }
        return json.dumps(json_record)


string_formatter = logging.Formatter(
    f"%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
json_formatter = JsonFormatter()


def get_file_handler_detailed():
    path_detailed_logs = os.path.join(ROOT_DIR, f"../logs/log_detailed_{settings.TITLE}.log")
    file_handler = TimedRotatingFileHandler(
        filename=path_detailed_logs,
        when='D',
        interval=3,
        backupCount=0,
        encoding="utf-8",
        delay=False,
        utc=False,
        atTime=None
    )
    file_handler.setLevel(settings.LEVEL_LOGGER_HANDLER)
    file_handler.setFormatter(json_formatter)
    return file_handler


def get_file_handler_error():
    path_error_logs = os.path.join(ROOT_DIR, f"../logs/log_error_{settings.TITLE}.log")
    file_handler = logging.FileHandler(path_error_logs)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(json_formatter)
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(settings.LEVEL_LOGGER_HANDLER)
    stream_handler.setFormatter(ColoredFormatter(string_formatter._fmt))
    return stream_handler


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler_detailed())
    logger.addHandler(get_file_handler_error())
    logger.addHandler(get_stream_handler())

    return logger
