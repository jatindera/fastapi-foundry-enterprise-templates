uv run uvicorn app.main:app --reload
# Enterprise Agentic AI Framework on Microsoft Foundry

## Purpose

This project provides a lightweight enterprise framework for building, provisioning, invoking, and governing AI agents hosted on Microsoft Foundry.

Microsoft Foundry is the core agent platform. This framework adds the application and governance structure required to use Foundry agents consistently across enterprise use cases.

The framework is designed to support:

- Multiple business agents in a single platform
- Configuration-driven agent provisioning
- FastAPI-based runtime APIs
- Microsoft Agent Framework integration for agent communication
- Azure authentication patterns for local development, Azure hosting and CI/CD
- Future conversation persistence, audit, observability and approval controls

---

## Architecture Direction

```text
Agent Configuration Files
        ↓
Agent Provisioning Service
azure-ai-projects
        ↓
Microsoft Foundry
Versioned Prompt Agents
        ↓
FastAPI Runtime API
        ↓
Microsoft Agent Framework / FoundryAgent
        ↓
Business Applications or User Interfaces
        ↓
Future: Azure SQL, Audit, Observability and Governance
```

---

## Key Design Principles

| Principle | Description |
|---|---|
| Foundry-first | Microsoft Foundry owns the hosted agent definitions and versions. |
| Provisioning separated from runtime | Agent creation/update is not performed during FastAPI startup or user requests. |
| Configuration-driven agents | Agent definitions are maintained in YAML rather than hardcoded in application code. |
| Controlled runtime usage | FastAPI invokes an approved existing Foundry agent version. |
| Environment-aware configuration | Azure connectivity and physical model deployment mappings are kept separate from agent behavior. |
| Production-minded implementation | Even while building incrementally, code structure is intended to support enterprise use. |

---

## Technology Responsibilities

| Technology / Component | Responsibility |
|---|---|
| Microsoft Foundry | Hosts versioned Prompt Agents and model deployments |
| `azure-ai-projects` | Creates or updates Foundry agents during provisioning |
| Microsoft Agent Framework `FoundryAgent` | Communicates with existing Foundry agents at runtime |
| FastAPI | Exposes backend APIs to invoke approved agents |
| Microsoft Entra ID / Azure Identity | Authenticates local developers, managed identities and service principals |
| Azure SQL | Planned storage for conversations, audit events and provisioning metadata |
| CI/CD Pipeline | Planned controlled provisioning and promotion of agents |

---

## Current Implementation Status

| Capability | Status |
|---|---:|
| Backend FastAPI foundation | Implemented |
| Environment configuration through `.env` | Implemented |
| Azure credential provider | Implemented |
| YAML-based agent definition | Implemented |
| Environment-based model deployment mapping | Implemented |
| Foundry agent provisioning through `azure-ai-projects` | Implemented |
| Private endpoint connectivity to Foundry | Resolved |
| Test agent provisioned in Foundry | Implemented: `hello-world-agent:2` |
| Runtime agent binding through `active-agents.yaml` | Being added |
| FastAPI communication through Microsoft Agent Framework | In progress |
| Incoming user-token validation for FastAPI | Planned |
| Azure SQL conversation persistence | Planned |
| CI/CD-based provisioning | Planned |
| Observability and audit integration | Planned |

---

## Current Test Agent

The current development agent is:

```text
Agent name                    : hello-world-agent
Provisioned version for test  : hello-world-agent:2
```

Foundry maintains versions for the same named agent:

```text
hello-world-agent:1
hello-world-agent:2   ← latest active version after current provisioning
```

A later provisioning run may create a newer version if the agent definition changes.

---

## Project Structure

```text
/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── agents/                  # Runtime agent binding loader
│   │   ├── core/                    # Configuration, logging, errors and middleware
│   │   ├── foundry/                 # Foundry and Microsoft Agent Framework integration
│   │   ├── identity/                # Azure credential selection
│   │   ├── routes/                  # FastAPI endpoints
│   │   ├── schemas/                 # Pydantic request/response contracts
│   │   ├── security/                # Planned incoming user-token validation
│   │   ├── db/                      # Planned Azure SQL connectivity and data access
│   │   ├── services/                # Planned orchestration and business logic
│   │   └── observability/           # Planned tracing, metrics and audit support
│   │
│   ├── provisioning/                # Agent creation/update lifecycle
│   │   └── README.md
│   │
│   ├── tests/
│   ├── .env.example
│   ├── .gitignore
│   └── README.md
│
├── configs/
│   ├── agents/                      # Desired Foundry agent definitions
│   ├── environments/                # Environment-specific model mappings
│   ├── runtime/                     # Approved runtime agent/version bindings
│   └── policies/                    # Future governance configuration
│
└── README.md
```

---

## Configuration Model

The framework separates agent provisioning configuration from runtime invocation configuration.

| Configuration | Purpose | Example |
|---|---|---|
| `backend/.env` | Defines environment, Foundry endpoint and authentication mode | `APP_ENV=local`, `AZURE_AUTH_MODE=developer` |
| `configs/agents/<agent-name>.yaml` | Defines an agent to create or update | Instructions and logical model mapping |
| `configs/environments/<environment>.yaml` | Resolves logical model keys to physical Foundry deployments | `gpt-5.4-mini` |
| `configs/runtime/<environment>/active-agents.yaml` | Defines which existing Foundry agent version FastAPI may invoke | `hello-world-agent:2` |

### Example Lifecycle

```text
configs/agents/hello-world-agent.yaml
        +
configs/environments/local.yaml
        ↓
Provision using azure-ai-projects
        ↓
Microsoft Foundry creates/updates:
hello-world-agent:2
        ↓
configs/runtime/local/active-agents.yaml
records the approved runtime version
        ↓
FastAPI invokes that agent using Microsoft Agent Framework
```

---

## Provisioning and Runtime Separation

### Provisioning

Provisioning creates or updates agents in Foundry.

```text
Technology: azure-ai-projects
Location  : backend/provisioning/
Command   : uv run python -m provisioning.provision_agent hello-world-agent
```

Provisioning details are documented in:

```text
backend/provisioning/README.md
```

### Runtime Communication

Runtime communication sends user requests to already-created Foundry agents.

```text
Technology: FastAPI + Microsoft Agent Framework FoundryAgent
Endpoint  : POST /agents/{agent_name}/messages
```

Runtime invocation does not recreate the agent or redefine its instructions. The Foundry-managed agent definition remains authoritative.

---

## Authentication Approach

The framework supports multiple Azure authentication modes through `AZURE_AUTH_MODE`.

| Mode | Intended Usage |
|---|---|
| `developer` | Local development using Azure CLI identity |
| `managed_identity` | Backend hosted on Azure |
| `service_principal` | CI/CD or approved automation scenarios |
| `default` | Azure SDK default credential chain |

For local development:

```env
AZURE_AUTH_MODE=developer
```

Authenticate using:

```powershell
az login
```

---

## Current API Direction

The FastAPI runtime is being built to expose agent invocation through:

```http
POST /agents/{agent_name}/messages
```

Example target request:

```json
{
  "message": "Introduce yourself in one sentence."
}
```

Example target runtime resolution:

```text
agent_name: hello-world-agent
        ↓
configs/runtime/local/active-agents.yaml
        ↓
Foundry agent version: hello-world-agent:2
        ↓
Microsoft Agent Framework FoundryAgent
        ↓
Response returned by FastAPI
```

---

## Development Approach

This project is being built incrementally:

1. Establish FastAPI foundation.
2. Implement Azure credential handling.
3. Provision agents in Foundry through configuration.
4. Communicate with provisioned agents through Microsoft Agent Framework.
5. Add Entra ID validation for incoming API users.
6. Add Azure SQL conversation and audit persistence.
7. Add CI/CD-based provisioning and promotion controls.
8. Add production observability and governance controls.

Each capability is implemented and tested before introducing the next layer.

---

## Next Steps

| Next Step | Purpose |
|---|---|
| Complete FastAPI + `FoundryAgent` runtime call | Validate API communication with `hello-world-agent:2` |
| Add Entra ID user-token validation | Secure incoming FastAPI requests |
| Add Azure SQL persistence | Store conversations and audit records |
| Add CI/CD provisioning workflow | Control agent creation and version promotion |
| Add observability | Trace and monitor agent execution |

---

## Related Documentation

| Document | Purpose |
|---|---|
| `backend/README.md` | Backend setup, local execution and API usage |
| `backend/provisioning/README.md` | Agent provisioning flow and configuration |