import logging
import sys

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """
    Configure application logging.

    For now, logs go to stdout.
    Later we can connect this to OpenTelemetry/Application Insights.
    """

    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    logging.getLogger("uvicorn.access").setLevel(log_level)
    logging.getLogger("uvicorn.error").setLevel(log_level)