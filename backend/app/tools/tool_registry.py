from collections.abc import Callable
from typing import Any

from app.tools.project_status_tool import get_project_status


ToolCallable = Callable[..., Any]


LOCAL_TOOL_REGISTRY: dict[str, ToolCallable] = {
    "get_project_status": get_project_status,
}


def get_local_tools(tool_names: list[str]) -> list[ToolCallable]:
    """
    Resolve configured local tool names into executable Python callables.

    These callables must correspond to function-tool definitions already
    configured on the Foundry Prompt Agent.
    """

    resolved_tools: list[ToolCallable] = []
    unknown_tools: list[str] = []

    for tool_name in tool_names:
        tool = LOCAL_TOOL_REGISTRY.get(tool_name)

        if tool is None:
            unknown_tools.append(tool_name)
            continue

        resolved_tools.append(tool)

    if unknown_tools:
        raise ValueError(
            "Unknown local tools configured for runtime: "
            + ", ".join(unknown_tools)
        )

    return resolved_tools