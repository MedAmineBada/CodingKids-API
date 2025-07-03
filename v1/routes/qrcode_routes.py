from fastapi import APIRouter

router = APIRouter(prefix="/qrcode", tags=["qrcode"])


@router.get("/", tags=["qrcode"])
def return_qrcode():
    return {"Success": "Yay!"}
