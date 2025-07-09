"""
Module for handling QR Code generation and scanning.
"""

import base64
import hashlib
import os
import time

import qrcode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from sqlalchemy.ext.asyncio import AsyncSession

from envconfig import EnvFile
from v1.models.qrcode import QRCode
from v1.utils import compress_img


def get_key() -> bytes:
    """
    Converts and returns the encryption key.
    Key is fetched from .env file, converted to bytes then returned.
    """
    return hashlib.sha256(EnvFile.ENCRYPTION_KEY.encode()).digest()


def encrypt(data: str) -> str:
    """
    Encrypt the data to be suitable for QR Code usage.
    Encryption is in the AESGCM method using an encryption key.
    """

    aesgsm = AESGCM(get_key())

    # Generates a random 12-byte Initialization Vector (IV).
    iv = os.urandom(12)

    # Encrypts the data using AES-GCM (with no associated authenticated data).
    ciphertext = aesgsm.encrypt(iv, data.encode("utf-8"), None)

    # Prepends IV to the ciphertext and encodes the result in Base64 for transport.
    return base64.b64encode(iv + ciphertext).decode("utf-8")


def decrypt(data: str) -> str:
    """
    Decrypt the data read from the QR Code.
    """
    aesgcm = AESGCM(get_key())

    # Decodes the Base64-encoded string received
    decoded = base64.b64decode(data)

    # Extract 12-byte IV and ciphertext
    iv = decoded[:12]
    ciphertext = decoded[12:]

    # Decrypt and decode to UTF-8 string
    plaintext = aesgcm.decrypt(iv, ciphertext, None)
    return plaintext.decode("utf-8")


# A custom error for the QRCode Generator
class QRCodeGenerationError(Exception):
    pass


def generate_qrcode(data: str, student_id: int) -> str:
    """
    Encrypts input data then generates and saves a styled QR code image for a student.

    Returns the QR Code's path.
    """
    try:
        # Create a QR code instance.
        qr = qrcode.QRCode(
            version=None,  # Auto-adjust size
            error_correction=qrcode.ERROR_CORRECT_H,  # High error correction
            box_size=10,
            border=1,
            image_factory=StyledPilImage,
            mask_pattern=None,
        )

        # Encrypt the data and add it to the QR code
        qr.add_data(encrypt(data))
        qr.make(fit=True)

        # Generate the image with style and embedded logo
        img = qr.make_image(
            color_mask=SolidFillColorMask(
                front_color=(0, 0, 0),
                back_color=(255, 255, 255),
            ),
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=EnvFile.CK_LOGO_DIR,
        )

        # Create a file path for temporary image and save it
        path = f"{EnvFile.QR_CODE_SAVE_DIR}/TEMP-{student_id}-{time.time()}.webp"
        img.save(path)

        # Compress the image, return its path and remove the temporary image.
        comp_qr_path = f"{EnvFile.QR_CODE_SAVE_DIR}/QR{student_id}-{time.time()}.webp"
        compress_img(path, comp_qr_path)

        os.remove(path)
        return comp_qr_path
    except Exception as e:
        raise QRCodeGenerationError(
            f"Could not generate QR code for user {student_id}: {e}"
        )


class QRCodeDeletionError(Exception):
    pass


class QRCodeNotFoundInDB(Exception):
    pass


async def delete_qr(id: int, session: AsyncSession):
    try:
        qrcode = await session.get(QRCode, id)
        if not qrcode:
            raise QRCodeNotFoundInDB()

        path = qrcode.url
        os.remove(path)

    except FileNotFoundError:
        raise FileNotFoundError()
    except QRCodeNotFoundInDB:
        raise QRCodeNotFoundInDB()
    except:
        raise QRCodeDeletionError()
