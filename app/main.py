from fastapi import FastAPI

from app.api.router import router


def create_app() -> FastAPI:
    application = FastAPI(title="Payment Service")
    application.include_router(router, prefix="/api")
    return application


app = create_app()
