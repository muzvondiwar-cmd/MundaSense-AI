from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": record.levelname,
            "event": record.getMessage(),
        }
        for key in ("model_version", "rules_version", "error_category"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO", log_dir: Path | None = None) -> logging.Logger:
    logger = logging.getLogger("mundasense")
    if logger.handlers:
        return logger
    logger.setLevel(level)
    handler: logging.Handler
    if log_dir is None:
        handler = logging.StreamHandler()
    else:
        log_dir.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_dir / "mundasense.jsonl", encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.propagate = False
    return logger
