from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_CONFIG_DIRECTORY = PROJECT_ROOT / "configs" / "runtime"


class RuntimeAgentBinding(BaseModel):
    """
    Runtime-approved Foundry agent that FastAPI is allowed to invoke.

    If agent_version is omitted, the latest active Foundry version is used.
    """

    model_config = ConfigDict(extra="forbid")

    foundry_agent_name: str = Field(min_length=1)
    agent_version: str | None = Field(
    default=None,
    min_length=1,
    description="Optional Foundry agent version. Omit to use the latest active version.",
    )
    enabled: bool = True
    local_tools: list[str] = Field(default_factory=list)


class RuntimeAgentRegistry(BaseModel):
    """
    Runtime mappings for agents available in a specific environment.
    """

    model_config = ConfigDict(extra="forbid")

    environment: str = Field(min_length=1)
    agents: dict[str, RuntimeAgentBinding]


def _load_yaml_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Runtime agent configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        content = yaml.safe_load(file)

    if not isinstance(content, dict):
        raise ValueError(
            f"Runtime agent configuration file must contain a YAML object: {path}"
        )

    return content


def load_runtime_agent_registry(environment: str) -> RuntimeAgentRegistry:
    """
    Load runtime-approved agent bindings for the selected environment.
    """

    path = RUNTIME_CONFIG_DIRECTORY / environment / "active-agents.yaml"

    try:
        registry = RuntimeAgentRegistry.model_validate(_load_yaml_file(path))
    except ValidationError as exc:
        raise ValueError(
            f"Invalid runtime agent configuration in {path}: {exc}"
        ) from exc

    if registry.environment != environment:
        raise ValueError(
            f"Runtime environment mismatch. Expected '{environment}' "
            f"but configuration contains '{registry.environment}'."
        )

    return registry


def get_runtime_agent_binding(
    agent_key: str,
    environment: str,
) -> RuntimeAgentBinding:
    """
    Resolve an API agent identifier into an approved Foundry agent version
    and its local runtime tool implementations.
    """

    registry = load_runtime_agent_registry(environment)
    binding = registry.agents.get(agent_key)

    if binding is None:
        raise KeyError(
            f"Agent '{agent_key}' is not configured for runtime use "
            f"in environment '{environment}'."
        )

    if not binding.enabled:
        raise PermissionError(
            f"Agent '{agent_key}' is disabled for runtime use."
        )

    return binding