import logging

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.sdk.resources import Resource

from app.core.config import Settings


logger = logging.getLogger(__name__)

_TELEMETRY_CONFIGURED = False
AUDIT_LOGGER_NAME = "app.audit"


def configure_application_insights(settings: Settings) -> None:
    """
    Configure FastAPI application telemetry export to Azure Application Insights.

    Foundry agent tracing is configured through the Foundry project connection
    to Application Insights. This configuration adds telemetry for the FastAPI
    application layer.

    Prompt content, response content, and tool payloads must not be written
    intentionally to application audit logs by default.
    """

    global _TELEMETRY_CONFIGURED

    if _TELEMETRY_CONFIGURED:
        return

    if not settings.observability_enabled:
        logger.info("FastAPI Application Insights telemetry is disabled.")
        return

    connection_string = settings.require_applicationinsights_connection_string()

    configure_azure_monitor(
        connection_string=connection_string,
        resource=Resource.create(
            {
                "service.name": settings.app_name,
                "deployment.environment.name": settings.app_env,
            }
        ),
        logger_name=AUDIT_LOGGER_NAME,
    )

    _TELEMETRY_CONFIGURED = True

    logger.info(
        "FastAPI Application Insights telemetry configured. "
        "service_name=%s environment=%s",
        settings.app_name,
        settings.app_env,
    )