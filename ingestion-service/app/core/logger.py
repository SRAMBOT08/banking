import logging
import sys
import json

from pythonjsonlogger import jsonlogger


def get_logger(name: str):
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
        handler.setFormatter(fmt)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
