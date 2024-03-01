import logging as _logging

import structlog

logger: structlog.typing.FilteringBoundLogger = structlog.get_logger()

_logging.basicConfig(
    level=_logging.ERROR,
)
