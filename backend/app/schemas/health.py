from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(..., description="API health status.")
    app_name: str = Field(..., description="Application name.")
    environment: str = Field(..., description="Application environment.")