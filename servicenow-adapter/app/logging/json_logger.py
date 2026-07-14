import logging
import re
import sys

from pythonjsonlogger import jsonlogger


_SECRET_PATTERN = re.compile(r"(password|token|authorization|api[_-]?key)", re.IGNORECASE)


class SecretMaskingFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str) and _SECRET_PATTERN.search(record.msg):
            record.msg = _SECRET_PATTERN.sub("***", record.msg)
        if isinstance(record.args, dict):
            record.args = {key: ("***" if _SECRET_PATTERN.search(str(key)) else value) for key, value in record.args.items()}
        return True


def get_logger(name: str, level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    handler.addFilter(SecretMaskingFilter())
    logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    return logger
