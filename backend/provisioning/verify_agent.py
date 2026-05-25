import argparse
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.foundry.agent_runtime_service import AgentRuntimeService
from app.foundry.project_client_factory import open_foundry_project_client
from provisioning.agent_config_loader import resolve_agent_config


logger = logging.getLogger(__name__)


def verify_agent(agent_key: str) -> None:
    settings = get_settings()
    configure_logging(settings)

    resolved_config = resolve_agent_config(
        agent_key=agent_key,
        environment=settings.app_env,
    )

    agent_config = resolved_config.agent

    if not agent_config.smoke_test.enabled:
        raise ValueError(
            f"Smoke testing is disabled for agent '{agent_key}'."
        )

    with open_foundry_project_client(settings) as project_client:
        runtime_service = AgentRuntimeService(project_client)

        result = runtime_service.start_conversation(
            agent_name=agent_config.foundry.agent_name,
            prompt=agent_config.smoke_test.prompt,
        )

    print()
    print("Foundry agent runtime verification completed successfully.")
    print(f"Framework agent key : {agent_config.agent_key}")
    print(f"Foundry agent name   : {result.agent_name}")
    print(f"Conversation ID      : {result.conversation_id}")
    print(f"Response ID          : {result.response_id}")
    print()
    print("Agent response:")
    print(result.output_text)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a smoke test against a provisioned Foundry agent."
    )
    parser.add_argument(
        "agent_key",
        help="Logical agent key matching configs/agents/<agent_key>.yaml",
    )

    args = parser.parse_args()

    try:
        verify_agent(args.agent_key)
    except Exception:
        logger.exception(
            "Foundry agent runtime verification failed. agent_key=%s",
            args.agent_key,
        )
        raise


if __name__ == "__main__":
    main()