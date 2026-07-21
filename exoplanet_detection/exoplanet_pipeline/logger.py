"""
Structured logging setup for the exoplanet detection pipeline.

Provides JSON or human-readable console output, optional rotating file logs,
and run-scoped context fields (run_id, target_id, stage).
"""

from __future__ import annotations

import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from exoplanet_pipeline import config

# Context propagated through async / threaded pipeline stages
_log_context: ContextVar[dict[str, Any]] = ContextVar("log_context", default={})


class JsonFormatter(logging.Formatter):
    """Emit one JSON object per log record for machine-readable logs."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if config.LOG_INCLUDE_CALLER:
            payload["module"] = record.module
            payload["function"] = record.funcName
            payload["line"] = record.lineno

        context = _log_context.get()
        if context:
            payload.update(context)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        for key, value in record.__dict__.items():
            if key.startswith("_") or key in {
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "exc_info",
                "exc_text",
                "stack_info",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "message",
            }:
                continue
            if key not in payload:
                payload[key] = value

        return json.dumps(payload, default=str)


class TextFormatter(logging.Formatter):
    """Human-readable formatter with optional context suffix."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        context = _log_context.get()
        if not context:
            return base

        context_str = " ".join(f"{k}={v}" for k, v in context.items())
        return f"{base} [{context_str}]"


def bind_context(**fields: Any) -> None:
    """Merge fields into the current logging context."""
    current = dict(_log_context.get())
    current.update(fields)
    _log_context.set(current)


def clear_context() -> None:
    """Reset logging context (e.g. between pipeline runs)."""
    _log_context.set({})


def unbind_context(*keys: str) -> None:
    """Remove specific keys from the logging context."""
    current = dict(_log_context.get())
    for key in keys:
        current.pop(key, None)
    _log_context.set(current)


def new_run_id() -> str:
    """Generate and bind a fresh run identifier."""
    run_id = uuid.uuid4().hex[:12]
    bind_context(run_id=run_id)
    return run_id


def _build_formatter() -> logging.Formatter:
    if config.LOG_FORMAT.lower() == "json":
        return JsonFormatter()
    return TextFormatter()


def _build_file_handler(log_path: Path) -> RotatingFileHandler:
    handler = RotatingFileHandler(
        log_path,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(JsonFormatter())
    handler.setLevel(getattr(logging, config.LOG_LEVEL.upper(), logging.INFO))
    return handler


def setup_logging(
    *,
    level: str | None = None,
    log_format: str | None = None,
    log_to_console: bool | None = None,
    log_to_file: bool | None = None,
    log_file: Path | str | None = None,
    logger_name: str | None = None,
) -> logging.Logger:
    """
    Configure and return the pipeline root logger.

    Parameters
    ----------
    level:
        Log level name (DEBUG, INFO, …). Defaults to ``config.LOG_LEVEL``.
    log_format:
        ``"json"`` or ``"text"``. Defaults to ``config.LOG_FORMAT``.
    log_to_console:
        Enable stderr stream handler. Defaults to ``config.LOG_TO_CONSOLE``.
    log_to_file:
        Enable rotating file handler. Defaults to ``config.LOG_TO_FILE``.
    log_file:
        Override log file path. Defaults to ``config.LOGS_DIR / config.LOG_FILE_NAME``.
    logger_name:
        Logger name. Defaults to ``config.PIPELINE_NAME``.
    """
    config.ensure_pipeline_dirs()

    resolved_level = getattr(logging, (level or config.LOG_LEVEL).upper(), logging.INFO)
    resolved_format = (log_format or config.LOG_FORMAT).lower()
    use_console = config.LOG_TO_CONSOLE if log_to_console is None else log_to_console
    use_file = config.LOG_TO_FILE if log_to_file is None else log_to_file
    name = logger_name or config.PIPELINE_NAME

    logger = logging.getLogger(name)
    logger.setLevel(resolved_level)
    logger.handlers.clear()
    logger.propagate = False

    formatter: logging.Formatter
    if resolved_format == "json":
        formatter = JsonFormatter()
    else:
        formatter = TextFormatter()

    if use_console:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(formatter)
        console.setLevel(resolved_level)
        logger.addHandler(console)

    log_path: Path | None = None
    if use_file:
        log_path = Path(log_file) if log_file else config.LOGS_DIR / config.LOG_FILE_NAME
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = _build_file_handler(log_path)
        logger.addHandler(file_handler)

    logger.debug(
        "Logging initialized",
        extra={
            "pipeline_version": config.PIPELINE_VERSION,
            "level": logging.getLevelName(resolved_level),
            "format": resolved_format,
            "log_file": str(log_path) if log_path is not None else None,
        },
    )

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a child logger under the pipeline namespace.

    If the root pipeline logger has no handlers yet, ``setup_logging`` is
    called automatically.
    """
    root = logging.getLogger(config.PIPELINE_NAME)
    if not root.handlers:
        setup_logging()

    if name is None or name == config.PIPELINE_NAME:
        return root

    if name.startswith(f"{config.PIPELINE_NAME}."):
        return logging.getLogger(name)

    return logging.getLogger(f"{config.PIPELINE_NAME}.{name}")


class LogContext:
    """Context manager that binds temporary logging fields."""

    def __init__(self, **fields: Any) -> None:
        self._fields = fields
        self._previous: dict[str, Any] = {}

    def __enter__(self) -> LogContext:
        self._previous = dict(_log_context.get())
        bind_context(**self._fields)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        _log_context.set(self._previous)


def log_stage(logger: logging.Logger, stage: str, message: str, **extra: Any) -> None:
    """Log a pipeline stage event with standard context fields."""
    with LogContext(stage=stage):
        logger.info(message, extra=extra)


def log_metric(
    logger: logging.Logger,
    metric: str,
    value: float | int | str,
    **extra: Any,
) -> None:
    """Log a numeric or scalar pipeline metric in structured form."""
    logger.info(
        f"metric {metric}={value}",
        extra={"metric": metric, "value": value, **extra},
    )
