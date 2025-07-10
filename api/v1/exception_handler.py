from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette import status

from api.v1.exceptions import AppException


async def custom_app_exception_handler(request: Request, exc: AppException):
    if isinstance(exc, AppException):
        # Handle custom exceptions
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    elif isinstance(exc, SQLAlchemyError):
        # Handle DB-related errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "A database error occurred."},
        )
    elif isinstance(exc, FileNotFoundError):
        # Handle File-related errors
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "File not found."},
        )
    else:
        # All other errors
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Something went wrong."},
        )
