from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error_code: str = Field(..., description="Application-level error code.")
    message: str = Field(..., description="Human-readable error message.")
    request_id: str | None = Field(default=None, description="Request correlation ID.")