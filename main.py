"""
Main application module.

This module initializes the FastAPI app, sets up the database connection
on startup,includes the versioned API routes."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.v1 import router
from api.v1.exception_handler import custom_app_exception_handler
from api.v1.exceptions import AppException
from db.db_initializer import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle the application's lifespan events.

    Initializes the database before the application starts accepting requests.
    """
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)

# To be removed, for testing purposes early
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.add_exception_handler(AppException, custom_app_exception_handler)

app.include_router(router.router)
