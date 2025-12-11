import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import router
from .schemas import (
    SourceTypeSchema,
    SourceSchema,
    SearchResultSchema,
    ContentSchema,
    SearchQueryRequest,
)
from .manager import Manager, get_manager


def create_app() -> FastAPI:
    app = FastAPI(
        title="Semantic Index API",
        description="API for semantic search over indexed documents",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.include_router(router)
    return app
