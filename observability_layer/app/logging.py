# structlog JSON logging setup
# app/logging.py
import structlog
import logging
from pythonjsonlogger import jsonlogger

def configure_logging(level="INFO"):
    # python std logging
    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    handler.setFormatter(fmt)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers = [handler]

    # structlog config
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

configure_logging()
log = structlog.get_logger()
