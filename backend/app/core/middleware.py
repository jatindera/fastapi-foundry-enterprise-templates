import time
import uuid
import logging

from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


def register_middlewares(app: FastAPI) -> None:
    """
    Register application middlewares.

    CORS is permissive for now because frontend is not built yet.
    We will tighten this later.
    """

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context_middleware(request: Request, call_next):
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        response.headers["x-request-id"] = request_id

        logger.info(
            "request completed method=%s path=%s status_code=%s duration_ms=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
            request_id,
        )

        return response