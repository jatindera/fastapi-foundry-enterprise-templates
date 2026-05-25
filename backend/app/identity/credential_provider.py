import logging

from azure.core.credentials import TokenCredential
from azure.identity import (
    AzureCliCredential,
    ClientSecretCredential,
    DefaultAzureCredential,
    ManagedIdentityCredential,
)

from app.core.config import Settings
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import (
    AzureCliCredential as AsyncAzureCliCredential,
    ClientSecretCredential as AsyncClientSecretCredential,
    DefaultAzureCredential as AsyncDefaultAzureCredential,
    ManagedIdentityCredential as AsyncManagedIdentityCredential,
)


logger = logging.getLogger(__name__)


def create_azure_credential(settings: Settings) -> TokenCredential:
    """
    Create an Azure credential based on AZURE_AUTH_MODE.

    Supported modes:
    - developer: Azure CLI signed-in user for local development
    - managed_identity: system-assigned or user-assigned managed identity
    - service_principal: explicit tenant/client/secret authentication
    - default: standard Azure SDK chained authentication behavior
    """

    settings.validate_azure_auth_configuration()

    logger.info(
        "Creating Azure credential. auth_mode=%s",
        settings.azure_auth_mode,
    )

    if settings.azure_auth_mode == "developer":
        return AzureCliCredential()

    if settings.azure_auth_mode == "managed_identity":
        if settings.azure_managed_identity_client_id:
            return ManagedIdentityCredential(
                client_id=settings.azure_managed_identity_client_id
            )

        return ManagedIdentityCredential()

    if settings.azure_auth_mode == "service_principal":
        return ClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
        )

    if settings.azure_auth_mode == "default":
        if settings.azure_managed_identity_client_id:
            return DefaultAzureCredential(
                managed_identity_client_id=(
                    settings.azure_managed_identity_client_id
                )
            )

        return DefaultAzureCredential()

    raise ValueError(
        f"Unsupported AZURE_AUTH_MODE: {settings.azure_auth_mode}"
    )

def create_azure_async_credential(settings: Settings) -> AsyncTokenCredential:
    """
    Create an asynchronous Azure credential for async Foundry runtime operations.
    """

    settings.validate_azure_auth_configuration()

    logger.info(
        "Creating async Azure credential. auth_mode=%s",
        settings.azure_auth_mode,
    )

    if settings.azure_auth_mode == "developer":
        return AsyncAzureCliCredential()

    if settings.azure_auth_mode == "managed_identity":
        if settings.azure_managed_identity_client_id:
            return AsyncManagedIdentityCredential(
                client_id=settings.azure_managed_identity_client_id
            )

        return AsyncManagedIdentityCredential()

    if settings.azure_auth_mode == "service_principal":
        return AsyncClientSecretCredential(
            tenant_id=settings.azure_tenant_id,
            client_id=settings.azure_client_id,
            client_secret=settings.azure_client_secret,
        )

    if settings.azure_auth_mode == "default":
        if settings.azure_managed_identity_client_id:
            return AsyncDefaultAzureCredential(
                managed_identity_client_id=settings.azure_managed_identity_client_id
            )

        return AsyncDefaultAzureCredential()

    raise ValueError(
        f"Unsupported AZURE_AUTH_MODE: {settings.azure_auth_mode}"
    )