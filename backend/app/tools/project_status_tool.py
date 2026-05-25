import logging


logger = logging.getLogger(__name__)


def get_project_status(project_id: str) -> str:
    """
    Return the current status of a project.

    This is an in-memory implementation used to validate the Foundry
    function-tool invocation flow. It will later be replaced by a
    database or API-backed implementation.
    """

    normalized_project_id = project_id.strip().upper()

    project_statuses = {
        "CAP-001": "In Progress - Architecture validation is underway.",
        "CAP-002": "Completed - The project has been delivered successfully.",
        "CAP-003": "On Hold - Awaiting business approval before proceeding.",
    }

    logger.info(
        "Executing local tool. tool_name=get_project_status project_id=%s",
        normalized_project_id,
    )

    status = project_statuses.get(normalized_project_id)

    if status is None:
        return (
            f"No status record was found for project '{normalized_project_id}'."
        )

    return f"Project {normalized_project_id}: {status}"