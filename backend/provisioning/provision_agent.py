import argparse
import logging

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.foundry.project_client_factory import open_foundry_project_client
from provisioning.agent_config_loader import resolve_agent_config
from provisioning.agent_provisioning_service import AgentProvisioningService


logger = logging.getLogger(__name__)


def provision_agent(agent_key: str) -> None:
    settings = get_settings()
    configure_logging(settings)

    resolved_config = resolve_agent_config(
        agent_key=agent_key,
        environment=settings.app_env,
    )

    with open_foundry_project_client(settings) as project_client:
        service = AgentProvisioningService(project_client)
        result = service.provision_prompt_agent(resolved_config)

    print()
    print("Foundry agent provisioning completed successfully.")
    print(f"Framework agent key : {result.agent_key}")
    print(f"Foundry agent name   : {result.foundry_agent_name}")
    print(f"Foundry version      : {result.version}")

    if result.agent_id:
        print(f"Foundry agent ID     : {result.agent_id}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Provision a configured Microsoft Foundry prompt agent."
    )
    parser.add_argument(
        "agent_key",
        help="Logical agent key matching configs/agents/<agent_key>.yaml",
    )

    args = parser.parse_args()

    try:
        provision_agent(args.agent_key)
    except Exception:
        logger.exception(
            "Foundry agent provisioning failed. agent_key=%s",
            args.agent_key,
        )
        raise


if __name__ == "__main__":
    main()