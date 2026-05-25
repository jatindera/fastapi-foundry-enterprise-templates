import logging

from fastapi import APIRouter, Depends, Request, status

from app.agents.runtime_binding_loader import get_runtime_agent_binding
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.foundry.maf_agent_runtime_service import MafAgentRuntimeService
from app.schemas.agent import AgentMessageRequest, AgentMessageResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post(
    "/{agent_name}/messages",
    response_model=AgentMessageResponse,
)
async def send_message_to_agent(
    agent_name: str,
    payload: AgentMessageRequest,
    request: Request,
    settings: Settings = Depends(get_settings),
) -> AgentMessageResponse:
    """
    Send a single-turn user message to an approved Foundry Prompt Agent.
    """

    try:
        binding = get_runtime_agent_binding(
            agent_key=agent_name,
            environment=settings.app_env,
        )
    except KeyError as exc:
        raise AppError(
            message=f"Agent '{agent_name}' is not configured for runtime use.",
            error_code="AGENT_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
        ) from exc
    except PermissionError as exc:
        raise AppError(
            message=f"Agent '{agent_name}' is disabled for runtime use.",
            error_code="AGENT_DISABLED",
            status_code=status.HTTP_403_FORBIDDEN,
        ) from exc
    except (FileNotFoundError, ValueError) as exc:
        logger.exception(
            "Runtime agent registry could not be loaded. "
            "agent_name=%s environment=%s",
            agent_name,
            settings.app_env,
        )

        raise AppError(
            message="Runtime agent configuration could not be loaded.",
            error_code="AGENT_RUNTIME_CONFIG_ERROR",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    service = MafAgentRuntimeService(settings)

    try:
        result = await service.send_message(
            binding=binding,
            message=payload.message,
            conversation_id=payload.conversation_id,
        )
    except Exception as exc:
        logger.exception(
            "Microsoft Agent Framework execution failed. "
            "agent_name=%s foundry_agent_name=%s agent_version=%s",
            agent_name,
            binding.foundry_agent_name,
            binding.agent_version,
        )

        raise AppError(
            message="Unable to receive a response from the configured agent.",
            error_code="FOUNDRY_AGENT_EXECUTION_ERROR",
            status_code=status.HTTP_502_BAD_GATEWAY,
        ) from exc

    return AgentMessageResponse(
        request_id=getattr(request.state, "request_id", None),
        agent_name=agent_name,
        foundry_agent_name=result.foundry_agent_name,
        agent_version=result.agent_version,
        conversation_id=result.conversation_id,
        response_text=result.response_text,
    )