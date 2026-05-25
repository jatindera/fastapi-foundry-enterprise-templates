from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Literal

class FunctionToolSettings(BaseModel):
    """
    Configuration for a function tool registered on a Foundry Prompt Agent.

    The function definition is provisioned in Foundry.
    Its Python implementation will be supplied later by the FastAPI runtime.
    """

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parameters: dict[str, Any]
    strict: bool = True

class HostedToolSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["web_search", "code_interpreter"]

class FoundryAgentSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_name: str = Field(min_length=1)
    model_key: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    # following is optional because we want to allow agents without tools, and we want to avoid provisioning issues if tools are not ready at the time of agent provisioning
    function_tools: list[FunctionToolSettings] = Field(default_factory=list)
    # tools already hosted on Foundry
    hosted_tools: list[HostedToolSettings] = Field(default_factory=list)

class RuntimeSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allow_conversations: bool = True


class SmokeTestSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    prompt: str = Field(min_length=1)


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_key: str = Field(min_length=1)
    display_name: str = Field(min_length=1)
    description: str = Field(default="")
    enabled: bool = True
    foundry: FoundryAgentSettings
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    smoke_test: SmokeTestSettings


class ModelDeploymentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    deployment_name: str = Field(min_length=1)


class FoundryEnvironmentSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    models: dict[str, ModelDeploymentConfig]


class EnvironmentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    environment: str = Field(min_length=1)
    foundry: FoundryEnvironmentSettings


class ResolvedAgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent: AgentConfig
    model_deployment_name: str = Field(min_length=1)