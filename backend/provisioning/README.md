# Foundry Agent Provisioning

## Purpose

The `provisioning` module creates and updates Microsoft Foundry agents from configuration files.

Provisioning is intentionally separate from the FastAPI runtime:

| Area | Responsibility |
|---|---|
| Provisioning | Create or update versioned agents in Microsoft Foundry using `azure-ai-projects` |
| FastAPI runtime | Communicate with already-provisioned agents using Microsoft Agent Framework `FoundryAgent` |
| Azure SQL | Later store conversations, audit logs and provisioning metadata |

For local testing, provisioning is executed manually. In the target architecture, it will run through CI/CD.

---

## Provision an Agent

From the `backend` folder:

```powershell
uv run python -m provisioning.provision_agent hello-world-agent
```

The value `hello-world-agent` identifies the agent configuration file:

```text
../configs/agents/hello-world-agent.yaml
```

---

## Provisioning Flow

```text
provision_agent.py
    ↓
Load backend/.env
    ↓
Load configs/agents/hello-world-agent.yaml
    ↓
Load configs/environments/local.yaml
    ↓
Resolve model_key to the actual Foundry model deployment
    ↓
Create Azure credential based on AZURE_AUTH_MODE
    ↓
Create AIProjectClient
    ↓
Create or update the Foundry agent version
```

---

## Agent Version Behavior

Foundry maintains versions of the same named agent.

```text
hello-world-agent:1
hello-world-agent:2   ← current/latest active version
```

- The first provisioning creates version `1`.
- Running provisioning after changing the agent definition creates the next version.
- The latest version becomes active automatically in Foundry.
- Earlier versions remain available for explicit use when required.

---

## Configuration Files

| File | Purpose | Used By |
|---|---|---|
| `backend/.env` | Environment and Azure connectivity settings | Provisioning and runtime |
| `configs/agents/hello-world-agent.yaml` | Agent definition and instructions | Provisioning |
| `configs/environments/local.yaml` | Actual model deployment mapping for the local environment | Provisioning |
| `configs/runtime/local/active-agents.yaml` | Approved agent version to invoke from FastAPI | Runtime |

---

## 1. Environment and Connectivity Settings

File:

```text
backend/.env
```

Purpose:

> Defines the environment and how the application authenticates and connects to Azure.

Example:

```env
APP_ENV=local
AZURE_AUTH_MODE=developer

FOUNDRY_PROJECT_ENDPOINT=https://<resource-name>.services.ai.azure.com/api/projects/<project-name>

AZURE_TENANT_ID=
AZURE_CLIENT_ID=
AZURE_CLIENT_SECRET=
AZURE_MANAGED_IDENTITY_CLIENT_ID=
```

Agent-specific details such as instructions and model mapping are intentionally not stored in `.env`.

---

## 2. Agent Definition

File:

```text
configs/agents/hello-world-agent.yaml
```

Purpose:

> Defines the agent that should be created or updated in Foundry.

Example:

```yaml
agent_key: hello-world-agent
display_name: Hello World Agent
description: Initial prompt agent used to validate framework provisioning and runtime execution.

enabled: true

foundry:
  agent_name: hello-world-agent
  model_key: hello-world-model-key
  instructions: |
    You are a helpful enterprise assistant.
    Answer questions clearly and professionally.

runtime:
  allow_conversations: true

smoke_test:
  enabled: true
  prompt: Explain Microsoft Foundry Agent Service in two simple sentences.
```

| Field | Meaning |
|---|---|
| `agent_key` | Framework identifier used by provisioning code |
| `foundry.agent_name` | Name of the agent created in Foundry |
| `foundry.model_key` | Logical model mapping identifier |
| `foundry.instructions` | Instructions stored in the Foundry agent |
| `enabled` | Whether the agent can be provisioned |
| `smoke_test.prompt` | Prompt for future post-provisioning validation |

---

## 3. Environment Model Mapping

File:

```text
configs/environments/local.yaml
```

Purpose:

> Maps the logical `model_key` from the agent definition to the actual deployed Foundry model.

Example:

```yaml
environment: local

foundry:
  models:
    hello-world-model-key:
      deployment_name: gpt-5.4-mini
```

This means:

```text
hello-world-agent
    uses model_key: hello-world-model-key
        ↓
local environment resolves it to:
    deployment_name: gpt-5.4-mini
```

Keeping this mapping separate allows different environments to use different model deployments without changing the agent definition.

---

## 4. Runtime Active Agent Binding

File:

```text
configs/runtime/local/active-agents.yaml
```

Purpose:

> Identifies which already-created Foundry agent version FastAPI is permitted to invoke.

Example:

```yaml
environment: local

agents:
  hello-world-agent:
    foundry_agent_name: hello-world-agent
    agent_version: "2"
    enabled: true
```

### Important Distinction

`active-agents.yaml` is **not used to create the agent**.

| File | Responsibility |
|---|---|
| `configs/agents/hello-world-agent.yaml` | Defines the agent to create or update |
| `configs/environments/local.yaml` | Defines the model deployment used during provisioning |
| `configs/runtime/local/active-agents.yaml` | Defines the existing agent version FastAPI should invoke |

The sequence is:

```text
Define agent YAML
    ↓
Provision agent using azure-ai-projects
    ↓
Foundry creates/updates hello-world-agent
    ↓
Add or update approved version in active-agents.yaml
    ↓
FastAPI invokes that version using Microsoft Agent Framework
```

### Why Maintain a Runtime Version Entry?

Foundry automatically activates the latest created version. However, explicitly recording the runtime version allows the application to control which version it invokes.

For example:

```text
hello-world-agent:1
hello-world-agent:2
```

The runtime may continue using version `1` until version `2` is tested and approved, or switch back if rollback is required.

---

## Files Used by Provisioning

| File | Responsibility |
|---|---|
| `provisioning/provision_agent.py` | Command-line entry point to provision one agent |
| `provisioning/agent_config_loader.py` | Loads and resolves YAML configuration |
| `provisioning/schemas.py` | Validates YAML configuration using Pydantic |
| `provisioning/agent_provisioning_service.py` | Calls Foundry to create or update an agent version |
| `app/core/config.py` | Loads settings from `.env` |
| `app/identity/credential_provider.py` | Selects the Azure authentication method |
| `app/foundry/project_client_factory.py` | Creates authenticated `AIProjectClient` instances |

---

## Foundry SDK Operation

Agent creation or update is performed through `azure-ai-projects`:

```python
project_client.agents.create_version(
    agent_name=agent_config.foundry.agent_name,
    definition=PromptAgentDefinition(
        model=config.model_deployment_name,
        instructions=agent_config.foundry.instructions,
    ),
)
```

`azure-ai-projects` is used for provisioning. FastAPI runtime communication with the created agent is handled separately using Microsoft Agent Framework.

---

## Authentication Modes

Provisioning uses `AZURE_AUTH_MODE` from `.env`.

| Value | Intended Usage |
|---|---|
| `developer` | Local execution using Azure CLI login |
| `managed_identity` | Azure-hosted runtime scenarios |
| `service_principal` | CI/CD or approved automation |
| `default` | Azure SDK default credential chain |

For local testing:

```env
AZURE_AUTH_MODE=developer
```

Authenticate before provisioning:

```powershell
az login
```

---

## Current Status

The framework has successfully provisioned:

```text
Agent name     : hello-world-agent
Current version: hello-world-agent:2
```

For FastAPI runtime communication, add the active version entry:

```text
configs/runtime/local/active-agents.yaml
```

```yaml
environment: local

agents:
  hello-world-agent:
    foundry_agent_name: hello-world-agent
    agent_version: "2"
    enabled: true
```

FastAPI will use this binding to communicate with the existing Foundry agent through Microsoft Agent Framework `FoundryAgent`.

---

## End-to-End Sequence

```text
1. Define agent:
   configs/agents/hello-world-agent.yaml

2. Define model mapping:
   configs/environments/local.yaml

3. Provision agent:
   uv run python -m provisioning.provision_agent hello-world-agent

4. Foundry creates or updates:
   hello-world-agent:2

5. Record approved runtime version:
   configs/runtime/local/active-agents.yaml

6. Invoke the agent from FastAPI:
   POST /agents/hello-world-agent/messages
```

---

## Planned Production Enhancements

| Enhancement | Purpose |
|---|---|
| CI/CD execution | Provision agents through controlled pipelines |
| Configuration change detection | Avoid unnecessary new versions |
| Smoke tests | Validate agents after provisioning |
| Provisioning metadata storage | Record deployed version, status and configuration hash |
| Approval controls | Govern production version promotion |
| Azure SQL persistence | Store runtime conversations and audit logs |