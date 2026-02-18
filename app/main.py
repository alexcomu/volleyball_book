from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import FastAPI, Request, Response

from app.api.routers.exercises import router as exercises_router
from app.infrastructure.db.models import Base
from app.infrastructure.db.session import engine


def create_app() -> FastAPI:
    app = FastAPI(title="Volleyball Book API", version="0.1.0")

    Base.metadata.create_all(bind=engine)
    app.include_router(exercises_router)

    @app.middleware("http")
    async def request_id_middleware(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @app.get("/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
