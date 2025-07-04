from fastapi import APIRouter
from v1.services.qrcode_service import gen
from v1.models.student import Student

router = APIRouter(prefix="/qrcode", tags=["qrcode"])


@router.post("/generate", tags=["qrcode"])
def generate_qrcode(student: Student):
    gen("Student1")
