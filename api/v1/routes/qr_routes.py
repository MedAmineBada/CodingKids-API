from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.v1.models.student import StudentRead
from api.v1.services.qrcode_service import scan_qr
from db.session import get_session

router = APIRouter(prefix="/scan", tags=["QR Code"])


@router.post("/", response_model=StudentRead, status_code=status.HTTP_200_OK)
async def scan(
    qr: UploadFile = File(...), session: AsyncSession = Depends(get_session)
):
    return await scan_qr(qr, session)
