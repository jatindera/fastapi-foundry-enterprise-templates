from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]

AppEnvironment = Literal["local", "dev", "test", "prod"]
AzureAuthMode = Literal[
    "developer",
    "managed_identity",
    "service_principal",
    "default",
]


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Agent-specific configuration is intentionally excluded from this class.
    Individual agent definitions are loaded from YAML configuration files.
    """

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(
        default="enterprise-agentic-ai-framework-api",
        validation_alias="APP_NAME",
    )

    app_env: AppEnvironment = Field(
        default="local",
        validation_alias="APP_ENV",
    )

    log_level: str = Field(
        default="INFO",
        validation_alias="LOG_LEVEL",
    )

    observability_enabled: bool = Field(
        default=False,
        validation_alias="OBSERVABILITY_ENABLED",
    )

    applicationinsights_connection_string: str | None = Field(
        default=None,
        validation_alias="APPLICATIONINSIGHTS_CONNECTION_STRING",
    )

    azure_auth_mode: AzureAuthMode = Field(
        default="developer",
        validation_alias="AZURE_AUTH_MODE",
    )

    azure_tenant_id: str | None = Field(
        default=None,
        validation_alias="AZURE_TENANT_ID",
    )

    azure_client_id: str | None = Field(
        default=None,
        validation_alias="AZURE_CLIENT_ID",
    )

    azure_client_secret: str | None = Field(
        default=None,
        validation_alias="AZURE_CLIENT_SECRET",
    )

    azure_managed_identity_client_id: str | None = Field(
        default=None,
        validation_alias="AZURE_MANAGED_IDENTITY_CLIENT_ID",
    )

    foundry_project_endpoint: str | None = Field(
        default=None,
        validation_alias="FOUNDRY_PROJECT_ENDPOINT",
    )

    sql_server: str | None = Field(
        default=None,
        validation_alias="SQL_SERVER",
    )

    sql_database: str | None = Field(
        default=None,
        validation_alias="SQL_DATABASE",
    )

    entra_tenant_id: str | None = Field(
        default=None,
        validation_alias="ENTRA_TENANT_ID",
    )

    entra_api_audience: str | None = Field(
        default=None,
        validation_alias="ENTRA_API_AUDIENCE",
    )

    def require_foundry_endpoint(self) -> str:
        """
        Return the configured Foundry endpoint or fail clearly.
        """

        if not self.foundry_project_endpoint:
            raise ValueError(
                "FOUNDRY_PROJECT_ENDPOINT is required for Foundry operations."
            )

        return self.foundry_project_endpoint
    
    def require_applicationinsights_connection_string(self) -> str:
        """
        Return the Application Insights connection string or fail clearly
        when application observability is enabled.
        """

        if not self.applicationinsights_connection_string:
            raise ValueError(
                "APPLICATIONINSIGHTS_CONNECTION_STRING is required "
                "when OBSERVABILITY_ENABLED=true."
            )

        return self.applicationinsights_connection_string
    
    def validate_azure_auth_configuration(self) -> None:
        """
        Validate credential settings for the selected Azure authentication mode.
        """

        if self.azure_auth_mode != "service_principal":
            return

        required_values = {
            "AZURE_TENANT_ID": self.azure_tenant_id,
            "AZURE_CLIENT_ID": self.azure_client_id,
            "AZURE_CLIENT_SECRET": self.azure_client_secret,
        }

        missing_values = [
            name for name, value in required_values.items() if not value
        ]

        if missing_values:
            raise ValueError(
                "AZURE_AUTH_MODE=service_principal requires: "
                + ", ".join(missing_values)
            )


@lru_cache
def get_settings() -> Settings:
    return Settings()