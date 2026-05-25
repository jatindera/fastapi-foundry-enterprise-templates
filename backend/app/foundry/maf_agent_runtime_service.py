import logging
from dataclasses import dataclass

from agent_framework.foundry import FoundryAgent
from azure.ai.projects.aio import AIProjectClient as AsyncAIProjectClient

from app.agents.runtime_binding_loader import RuntimeAgentBinding
from app.core.config import Settings
from app.identity.credential_provider import (
    create_azure_async_credential,
    create_azure_credential,
)
from app.tools.tool_registry import get_local_tools
from azure.core.credentials_async import AsyncTokenCredential
from azure.identity.aio import (
    AzureCliCredential as AsyncAzureCliCredential,
    ClientSecretCredential as AsyncClientSecretCredential,
    DefaultAzureCredential as AsyncDefaultAzureCredential,
    ManagedIdentityCredential as AsyncManagedIdentityCredential,
)

logger = logging.getLogger(__name__)

# Function	Used For
# create_azure_credential()	Existing synchronous provisioning and current MAF path
# create_azure_async_credential()	Asynchronous Foundry conversation creation inside FastAPI


@dataclass(frozen=True)
class MafAgentResponseResult:
    """
    Internal service result returned after invoking a Foundry Prompt Agent.
    """

    foundry_agent_name: str
    agent_version: str | None
    response_text: str
    conversation_id: str


class MafAgentRuntimeService:
    """
    Invokes an existing Microsoft Foundry Prompt Agent through
    Microsoft Agent Framework.

    This service does not create or modify Foundry agents.
    Agent provisioning remains the responsibility of azure-ai-projects
    provisioning code and the future CI/CD pipeline.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def _create_foundry_conversation(self) -> str:
        """
        Create a portal-visible Foundry conversation and return its ID.
        """

        endpoint = self._settings.require_foundry_endpoint()
        credential = create_azure_async_credential(self._settings)

        try:
            async with AsyncAIProjectClient(
                endpoint=endpoint,
                credential=credential,
            ) as project_client:
                async with project_client.get_openai_client() as openai_client:
                    conversation = await openai_client.conversations.create()

            logger.info(
                "Created Foundry conversation. conversation_id=%s",
                conversation.id,
            )

            return conversation.id
        finally:
            await credential.close()

    async def send_message(
        self,
        binding: RuntimeAgentBinding,
        message: str,
        conversation_id: str | None = None,
    ) -> MafAgentResponseResult:
        """
        Send a message to an approved Foundry Prompt Agent.

        If conversation_id is omitted, a new Foundry conversation is created.
        If conversation_id is provided, the existing Foundry conversation is resumed.

        Function tools are executed locally in the FastAPI application only
        when they match tool definitions already registered on the Foundry agent.
        """

        endpoint = self._settings.require_foundry_endpoint()
        credential = create_azure_credential(self._settings)
        local_tools = get_local_tools(binding.local_tools)

        logger.info(
            "Invoking Foundry agent through Microsoft Agent Framework. "
            "agent_name=%s agent_version=%s local_tool_count=%s",
            binding.foundry_agent_name,
            binding.agent_version,
            len(local_tools),
        )

        try:
            agent = FoundryAgent(
                project_endpoint=endpoint,
                agent_name=binding.foundry_agent_name,
                agent_version=binding.agent_version,
                credential=credential,
                tools=local_tools,
            )

            resolved_conversation_id = (
                conversation_id
                if conversation_id
                else await self._create_foundry_conversation()
            )

            session = agent.get_session(
                service_session_id=resolved_conversation_id,
            )

            result = await agent.run(
                message,
                session=session,
            )

            logger.info(
                "Foundry agent response received through Microsoft Agent Framework. "
                "agent_name=%s agent_version=%s conversation_id=%s",
                binding.foundry_agent_name,
                binding.agent_version,
                resolved_conversation_id,
            )

            return MafAgentResponseResult(
                foundry_agent_name=binding.foundry_agent_name,
                agent_version=binding.agent_version,
                conversation_id=resolved_conversation_id,
                response_text=result.text,
            )
        finally:
            close_method = getattr(credential, "close", None)

            if callable(close_method):
                close_method()

    def create_azure_async_credential(settings: Settings) -> AsyncTokenCredential:
        """
        Create an asynchronous Azure credential for async Azure SDK operations.

        Used by asynchronous runtime operations such as creating a Foundry
        conversation through the AsyncOpenAI client.
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
                    managed_identity_client_id=(
                        settings.azure_managed_identity_client_id
                    )
                )

            return AsyncDefaultAzureCredential()

        raise ValueError(
            f"Unsupported AZURE_AUTH_MODE: {settings.azure_auth_mode}"
        )