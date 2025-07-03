# This file serves as the main route with all other routes in v1 connecting to it
from fastapi import APIRouter
from models import qrcode

router = APIRouter(prefix="/api/v1")

router.include_router()
