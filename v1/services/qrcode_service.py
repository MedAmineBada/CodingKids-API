import base64
import hashlib
import os
import qrcode
import time

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from envconfig import EnvFile


def gen_key() -> bytes:
    return hashlib.sha256(EnvFile.ENCRYPTION_KEY.encode()).digest()


def encrypt(data: str) -> str:
    aesgsm = AESGCM(gen_key())
    iv = os.urandom(12)
    ciphertext = aesgsm.encrypt(iv, data.encode("utf-8"), None)
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt(data: str) -> str:
    aesgcm = AESGCM(gen_key())
    decoded = base64.b64decode(data)
    iv = decoded[:12]
    ciphertext = decoded[12:]
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")


# A custom exception for errors that occur during qr code generation
class QRCodeGenerationError(Exception):
    pass


def generate_qrcode(data: str, student_id: int) -> str:
    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=16,
            border=1,
            image_factory=StyledPilImage,
            mask_pattern=None,
        )
        qr.add_data(encrypt(data))
        qr.make(fit=True)
        img = qr.make_image(
            color_mask=SolidFillColorMask(
                front_color=(255, 169, 0),
                back_color=(255, 255, 255),
            ),
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=EnvFile.CK_LOGO_DIR,
        )
        path = (
            f"{EnvFile.QR_CODE_SAVE_DIR}/Student_{student_id}_QRCode_{time.time()}.png"
        )
        img.save(path)
        return path
    except Exception as e:
        raise QRCodeGenerationError(
            f"Could not generate QR code for user {student_id}: {e}"
        )
