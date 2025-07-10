"""
Main application module.

This module initializes the FastAPI app, sets up the database connection
on startup,includes the versioned API routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.db_initializer import init_db
from v1 import router
from v1.exception_handler import custom_app_exception_handler
from v1.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle the application's lifespan events.

    Initializes the database before the application starts accepting requests.
    """
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)


app.add_exception_handler(AppException, custom_app_exception_handler)

app.include_router(router.router)
