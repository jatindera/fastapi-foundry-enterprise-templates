from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.schemas.system import SystemInfoResponse

router = APIRouter(tags=["System"])


@router.get("/system/info", response_model=SystemInfoResponse)
def get_system_info(settings: Settings = Depends(get_settings)) -> SystemInfoResponse:
    return SystemInfoResponse(
        app_name=settings.app_name,
        environment=settings.app_env,
        azure_auth_mode=settings.azure_auth_mode,
        foundry_configured=bool(settings.foundry_project_endpoint),
        sql_configured=bool(settings.sql_server and settings.sql_database),
        entra_configured=bool(
            settings.entra_tenant_id and settings.entra_api_audience
        ),
    )