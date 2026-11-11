from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from receipts.api import admin, changes, claims, events, meta, orgs
from receipts.settings import check_settings, get_settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    check_settings(get_settings())
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Ledgit API", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[o.strip() for o in settings.api_cors_origins.split(",") if o.strip()],
        allow_methods=["GET"],
        allow_headers=["*"],
    )
    for module in (meta, claims, orgs, events, changes):
        app.include_router(module.router, prefix="/api/v1")
    if settings.env == "local":
        app.include_router(admin.router, prefix="/api/v1")
    return app


app = create_app()
