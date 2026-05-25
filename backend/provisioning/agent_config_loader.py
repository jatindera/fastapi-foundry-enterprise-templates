import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from provisioning.schemas import (
    AgentConfig,
    EnvironmentConfig,
    ResolvedAgentConfig,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_CONFIG_DIRECTORY = PROJECT_ROOT / "configs" / "agents"
ENVIRONMENT_CONFIG_DIRECTORY = PROJECT_ROOT / "configs" / "environments"

AGENT_KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if not isinstance(content, dict):
        raise ValueError(
            f"Configuration file must contain a YAML object: {path}"
        )

    return content


def load_agent_config(agent_key: str) -> AgentConfig:
    """
    Load and validate an individual agent YAML configuration file.
    """

    if not AGENT_KEY_PATTERN.fullmatch(agent_key):
        raise ValueError(
            "agent_key must contain lowercase letters, numbers, and hyphens only."
        )

    path = AGENT_CONFIG_DIRECTORY / f"{agent_key}.yaml"

    try:
        config = AgentConfig.model_validate(_load_yaml_file(path))
    except ValidationError as exc:
        raise ValueError(
            f"Invalid agent configuration in {path}: {exc}"
        ) from exc

    if config.agent_key != agent_key:
        raise ValueError(
            f"Agent key mismatch. File requested '{agent_key}' "
            f"but configuration contains '{config.agent_key}'."
        )

    return config


def load_environment_config(environment: str) -> EnvironmentConfig:
    """
    Load and validate environment-specific Foundry model mappings.
    """

    path = ENVIRONMENT_CONFIG_DIRECTORY / f"{environment}.yaml"

    try:
        config = EnvironmentConfig.model_validate(_load_yaml_file(path))
    except ValidationError as exc:
        raise ValueError(
            f"Invalid environment configuration in {path}: {exc}"
        ) from exc

    if config.environment != environment:
        raise ValueError(
            f"Environment mismatch. Expected '{environment}' "
            f"but configuration contains '{config.environment}'."
        )

    return config


def resolve_agent_config(
    agent_key: str,
    environment: str,
) -> ResolvedAgentConfig:
    """
    Resolve logical agent configuration into a physical Foundry deployment
    configuration for the selected environment.
    """

    agent_config = load_agent_config(agent_key)
    environment_config = load_environment_config(environment)

    model_key = agent_config.foundry.model_key
    model_mapping = environment_config.foundry.models.get(model_key)

    if model_mapping is None:
        raise ValueError(
            f"Model key '{model_key}' used by agent '{agent_key}' "
            f"is not defined for environment '{environment}'."
        )

    return ResolvedAgentConfig(
        agent=agent_config,
        model_deployment_name=model_mapping.deployment_name,
    )