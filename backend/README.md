```markdown
# FastAPI Basic Template

A lightweight, production-ready FastAPI foundation. This template provides the core routing, exception handling, and structural boilerplate needed to build high-performance APIs without unnecessary bloat.

## Prerequisites

This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast project and dependency management. 

If you do not have `uv` installed, install it globally:

```bash
# macOS / Linux
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"

```

## Quickstart

### 1. Checkout the Tagged Release

If you cloned the full repository, ensure you checkout the specific tag for this template into a new working branch to avoid a detached HEAD state:

```bash
# Navigate to the project directory
cd your-repo

# Checkout the tag into a new local branch
git checkout tags/v1.0-fastapi-basic -b my-new-api

```

### 2. Sync the Environment

Run the sync command. `uv` will automatically read your `pyproject.toml`, resolve the dependency tree, generate a `uv.lock` file (if one doesn't exist), create a `.venv` directory, and install all required packages instantly.

```bash
uv sync

```

### 3. Run the Development Server

Instead of manually activating the virtual environment, use `uv run`. This command guarantees the application executes within the isolated project environment.

```bash
uv run uvicorn app.main:app --reload

```

*(If your core application file is located in a subdirectory, adjust the path, e.g., `uv run fastapi dev app/main.py`).*

## Accessing the Application

Once the server initializes, you can access the API and its auto-generated documentation:

* **API Root:** `http://127.0.0.1:8000`
* **Swagger UI (Interactive):** `http://127.0.0.1:8000/docs`
* **ReDoc:** `http://127.0.0.1:8000/redoc`

---------
# Provision Agents (hello-agent is name of agent)
uv run python -m provisioning.provision_agent hello-agent
