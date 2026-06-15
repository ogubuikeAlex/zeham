import json
import logging


class JsonLogFormatter(logging.Formatter):
    """Render each log record as a single JSON line."""

    _RESERVED = {
        'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename',
        'module', 'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName',
        'created', 'msecs', 'relativeCreated', 'thread', 'threadName',
        'processName', 'process', 'taskName',
    }

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            'ts': self.formatTime(record, '%Y-%m-%dT%H:%M:%S%z'),
            'level': record.levelname,
            'logger': record.name,
            'msg': record.getMessage(),
        }
        # Promote any structured fields passed via logger.info(..., extra={...}).
        for key, value in record.__dict__.items():
            if key not in self._RESERVED and not key.startswith('_'):
                payload[key] = value
        if record.exc_info:
            payload['exc'] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = 'INFO', json_output: bool = True) -> None:
    handler = logging.StreamHandler()
    if json_output:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
        )
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
