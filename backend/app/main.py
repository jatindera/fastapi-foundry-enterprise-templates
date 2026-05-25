from app.core.config import get_settings
from app.core.logging import configure_logging
from app.observability.application_insights import configure_application_insights


settings = get_settings()

configure_logging(settings)
configure_application_insights(settings)


# These imports intentionally occur after Application Insights configuration.
# Azure Monitor OpenTelemetry must be configured before FastAPI is imported
# so incoming API requests can be instrumented correctly.
from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.core.lifespan import lifespan
from app.core.middleware import register_middlewares
from app.routes import agents, health, system
from app.shared.constants import APP_DESCRIPTION, APP_TITLE, APP_VERSION


app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
)


register_middlewares(app)
register_exception_handlers(app)

app.include_router(health.router)
app.include_router(system.router)
app.include_router(agents.router)