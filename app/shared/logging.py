import json
import logging
from datetime import UTC, datetime
from typing import Any


def get_logger(name: str = "volleyball_book") -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
    return logger


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    payload = {
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload))
