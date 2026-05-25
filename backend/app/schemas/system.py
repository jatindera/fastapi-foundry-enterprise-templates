from pydantic import BaseModel, Field


class SystemInfoResponse(BaseModel):
    app_name: str = Field(..., description="Application name.")
    environment: str = Field(..., description="Application environment.")
    azure_auth_mode: str = Field(..., description="Configured Azure authentication mode.")
    foundry_configured: bool = Field(..., description="Whether Foundry settings are configured.")
    sql_configured: bool = Field(..., description="Whether Azure SQL settings are configured.")
    entra_configured: bool = Field(..., description="Whether Entra token validation settings are configured.")