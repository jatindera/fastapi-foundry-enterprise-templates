# Add a Foundry Agent with Web Search and Code Interpreter

## Goal

Create a new Foundry-managed agent that uses two **hosted tools**:

- **Web Search**: retrieves current public web information.
- **Code Interpreter**: runs Python in a Foundry-managed sandbox for calculations or analysis.

Agent name:

```text
research-analysis-agent
```

> These tools run in Foundry. No new FastAPI local tool implementation is required.

---

## Step 1 — Create Agent Configuration

Create:

```text
configs/agents/research-analysis-agent.yaml
```

Add:

```yaml
agent_key: research-analysis-agent
display_name: Research Analysis Agent
description: Agent used to validate Foundry-hosted Web Search and Code Interpreter tools.

enabled: true

foundry:
  agent_name: research-analysis-agent
  model_key: general-chat
  instructions: |
    You are a research and analysis assistant.
    Use web search when the user asks for current public information.
    Use code interpreter when calculations or data analysis are required.
    Keep responses clear and cite web-based findings when available.

  hosted_tools:
    - type: web_search
    - type: code_interpreter

runtime:
  allow_conversations: true

smoke_test:
  enabled: true
  prompt: Find a recent public update about Microsoft Foundry agents and calculate how many days have passed since its publication date.
```

No change is needed in `configs/environments/local.yaml` because this agent reuses the existing `hello-world-model-key` mapping.

---

## Step 2 — Extend Provisioning Schema

Open:

```text
backend/provisioning/schemas.py
```

### Update the import

Replace:

```python
from typing import Any
```

with:

```python
from typing import Any, Literal
```

### Add this new schema above `FoundryAgentSettings`

```python
class HostedToolSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["web_search", "code_interpreter"]
```

### Add this field inside `FoundryAgentSettings`

```python
hosted_tools: list[HostedToolSettings] = Field(default_factory=list)
```

Result: agent YAML can now declare Foundry-hosted tools without affecting existing agents.

---

## Step 3 — Extend the Provisioning Service

Open:

```text
backend/provisioning/agent_provisioning_service.py
```

### Update the SDK import

Replace the current `azure.ai.projects.models` import with:

```python
from azure.ai.projects.models import (
    CodeInterpreterTool,
    FunctionTool,
    PromptAgentDefinition,
    Tool,
    WebSearchTool,
)
```

### Add this method below `_build_function_tools(...)`

```python
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
```

### Change tool construction inside `provision_prompt_agent(...)`

Replace:

```python
tools = self._build_function_tools(config)
```

with:

```python
function_tools = self._build_function_tools(config)
hosted_tools = self._build_hosted_tools(config)
tools = function_tools + hosted_tools
```

### Update the provisioning log

Replace the `function_tool_count` log value with both counts:

```python
logger.info(
    "Provisioning Foundry prompt agent. agent_key=%s "
    "agent_name=%s model_deployment=%s function_tool_count=%s hosted_tool_count=%s",
    agent_config.agent_key,
    agent_config.foundry.agent_name,
    config.model_deployment_name,
    len(function_tools),
    len(hosted_tools),
)
```

The existing agent creation line remains unchanged:

```python
definition=PromptAgentDefinition(
    model=config.model_deployment_name,
    instructions=agent_config.foundry.instructions,
    tools=tools,
)
```

---

## Step 4 — Provision the Agent

From the `backend` folder, run:

```powershell
uv run python -m provisioning.provision_agent research-analysis-agent
```

Expected outcome:

```text
Foundry agent name : research-analysis-agent
Foundry version    : 1
Hosted tool count  : 2
```

---

## Step 5 — Add Runtime Entry

After provisioning succeeds, open:

```text
configs/runtime/local/active-agents.yaml
```

Add:

```yaml
  research-analysis-agent:
    foundry_agent_name: research-analysis-agent
    enabled: true
    local_tools: []
```

Do not add Web Search or Code Interpreter under `local_tools`; they run inside Foundry.

---

## Step 6 — Test Through FastAPI

No FastAPI code changes are required.

Run the existing API and invoke:

```http
POST /agents/research-analysis-agent/messages
```

Example request:

```json
{
  "message": "Search the public web for a recent Microsoft Foundry agents update, identify the publication date, and use Python to calculate how many days have passed from that date to today."
}
```

Expected behaviour:

```text
FastAPI invokes the existing Foundry agent
        ↓
Foundry performs web search
        ↓
Foundry uses Code Interpreter for the calculation
        ↓
FastAPI returns the final response
```

---

## Files Changed

| File | Change |
|---|---|
| `configs/agents/research-analysis-agent.yaml` | New agent with hosted tools |
| `backend/provisioning/schemas.py` | Add `hosted_tools` validation |
| `backend/provisioning/agent_provisioning_service.py` | Build `WebSearchTool()` and `CodeInterpreterTool()` |
| `configs/runtime/local/active-agents.yaml` | Expose provisioned agent to FastAPI |
| FastAPI runtime files | No change |

---

## Notes

- Web Search accesses current public web information; use non-sensitive test prompts.
- Code Interpreter runs in a Microsoft-managed sandbox and may incur additional charges.
- `CodeInterpreterTool()` is sufficient for this first no-file calculation test; file-based analysis can be added later.
