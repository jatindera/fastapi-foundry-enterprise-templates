from collections.abc import Iterator
from contextlib import contextmanager

from azure.ai.projects import AIProjectClient

from app.core.config import Settings
from app.identity.credential_provider import create_azure_credential


@contextmanager
def open_foundry_project_client(
    settings: Settings,
) -> Iterator[AIProjectClient]:
    """
    Open a Microsoft Foundry project client and close its Azure credential
    when the operation completes.
    """

    endpoint = settings.require_foundry_endpoint()
    credential = create_azure_credential(settings)

    try:
        with AIProjectClient(
            endpoint=endpoint,
            credential=credential,
        ) as project_client:
            yield project_client
    finally:
        close_method = getattr(credential, "close", None)

        if callable(close_method):
            close_method()