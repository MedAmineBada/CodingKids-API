"""
Main router module
Serves as the main route with all other routes in v1 connecting to it.

"""

from fastapi import APIRouter

from v1.routes import student_routes

router = APIRouter(prefix="/api/v1")

router.include_router(student_routes.router)


@router.get("/")
def index():
    return {"message": "Hello World"}
