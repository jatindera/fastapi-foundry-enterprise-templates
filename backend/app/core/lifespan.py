import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logger.info(
        "Starting application. app_name=%s app_env=%s azure_auth_mode=%s",
        settings.app_name,
        settings.app_env,
        settings.azure_auth_mode,
    )

    yield

    logger.info("Shutting down application. app_name=%s", settings.app_name)