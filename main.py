"""
Main application module.

This module initializes the FastAPI app, sets up the database connection
on startup,includes the versioned API routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse

from db.db_initializer import init_db
from v1 import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle the application's lifespan events.

    Initializes the database before the application starts accepting requests.
    """
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(router.router)
