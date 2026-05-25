import logging
from dataclasses import dataclass

from azure.ai.projects import AIProjectClient


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentResponseResult:
    agent_name: str
    conversation_id: str
    response_id: str
    output_text: str


class AgentRuntimeService:
    """
    Executes requests against an already provisioned Foundry agent.

    This service does not create or update agents.
    """

    def __init__(self, project_client: AIProjectClient) -> None:
        self._project_client = project_client

    def start_conversation(
        self,
        agent_name: str,
        prompt: str,
    ) -> AgentResponseResult:
        """
        Create a new Foundry conversation and send the first prompt.
        """

        logger.info(
            "Starting Foundry agent conversation. agent_name=%s",
            agent_name,
        )

        with self._project_client.get_openai_client() as openai_client:
            conversation = openai_client.conversations.create()

            response = openai_client.responses.create(
                conversation=conversation.id,
                extra_body={
                    "agent_reference": {
                        "name": agent_name,
                        "type": "agent_reference",
                    }
                },
                input=prompt,
            )

        logger.info(
            "Foundry agent response received. agent_name=%s "
            "conversation_id=%s response_id=%s",
            agent_name,
            conversation.id,
            response.id,
        )

        return AgentResponseResult(
            agent_name=agent_name,
            conversation_id=conversation.id,
            response_id=response.id,
            output_text=response.output_text,
        )