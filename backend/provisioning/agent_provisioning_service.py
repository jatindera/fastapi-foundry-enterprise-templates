import logging
from dataclasses import dataclass

from azure.ai.projects import AIProjectClient

from provisioning.schemas import ResolvedAgentConfig
from azure.ai.projects.models import (
    CodeInterpreterTool,
    FunctionTool,
    PromptAgentDefinition,
    Tool,
    WebSearchTool,
)


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProvisionedAgentResult:
    agent_key: str
    foundry_agent_name: str
    version: str
    agent_id: str | None


class AgentProvisioningService:
    """
    Creates Foundry agent versions from validated framework configuration.

    Provisioning is intentionally separate from FastAPI runtime execution.
    Later, this service can be invoked from CI/CD.
    """

    def __init__(self, project_client: AIProjectClient) -> None:
        self._project_client = project_client

    @staticmethod
    def _build_function_tools(
        config: ResolvedAgentConfig,
    ) -> list[Tool]:
        """
        Convert YAML-defined function tool configuration into Foundry SDK tools.
        """

        tools: list[Tool] = []

        for tool_config in config.agent.foundry.function_tools:
            tools.append(
                FunctionTool(
                    name=tool_config.name,
                    description=tool_config.description,
                    parameters=tool_config.parameters,
                    strict=tool_config.strict,
                )
            )

        return tools

    def provision_prompt_agent(
        self,
        config: ResolvedAgentConfig,
    ) -> ProvisionedAgentResult:
        agent_config = config.agent

        if not agent_config.enabled:
            raise ValueError(
                f"Agent '{agent_config.agent_key}' is disabled and cannot be provisioned."
            )

        function_tools = self._build_function_tools(config)
        hosted_tools = self._build_hosted_tools(config)
        tools = function_tools + hosted_tools

        logger.info(
            "Provisioning Foundry prompt agent. agent_key=%s "
            "agent_name=%s model_deployment=%s function_tool_count=%s hosted_tool_count=%s",
            agent_config.agent_key,
            agent_config.foundry.agent_name,
            config.model_deployment_name,
            len(function_tools),
            len(hosted_tools),
        )

        agent = self._project_client.agents.create_version(
            agent_name=agent_config.foundry.agent_name,
            definition=PromptAgentDefinition(
                model=config.model_deployment_name,
                instructions=agent_config.foundry.instructions,
                tools=tools,
            ),
        )

        result = ProvisionedAgentResult(
            agent_key=agent_config.agent_key,
            foundry_agent_name=agent.name,
            version=str(agent.version),
            agent_id=getattr(agent, "id", None),
        )

        logger.info(
            "Foundry agent version created. agent_key=%s "
            "agent_name=%s version=%s function_tool_count=%s",
            result.agent_key,
            result.foundry_agent_name,
            result.version,
            len(tools),
        )

        return result
    
    @staticmethod
    def _build_hosted_tools(
        config: ResolvedAgentConfig,
    ) -> list[Tool]:
        tools: list[Tool] = []

        for tool_config in config.agent.foundry.hosted_tools:
            if tool_config.type == "web_search":
                tools.append(WebSearchTool())
            elif tool_config.type == "code_interpreter":
                tools.append(CodeInterpreterTool())

        return tools