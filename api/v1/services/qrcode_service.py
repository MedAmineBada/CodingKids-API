"""
Module for handling QR Code generation and scanning.
"""

import base64
import hashlib
import io
import os
import time

import qrcode
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import UploadFile
from pyzbar.pyzbar import decode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.exceptions import (
    QRCodeNotFoundInDBError,
    FileTypeNotSupportedError,
    NotQRCodeError,
    StudentNotFoundError,
)
from api.v1.models.qrcode import QRCode
from api.v1.models.student import Student
from api.v1.utils import compress_img
from envconfig import EnvFile


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


def generate_qrcode(data: str, student_id: int) -> str:
    """
    Encrypts input data then generates and saves a styled QR code image for a student.

    Returns the QR Code's path.
    """

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


async def delete_qr(id: int, session: AsyncSession):
    """
    Handles deletion of a qr code
    """
    qrcode = await session.get(QRCode, id)
    if not qrcode:
        raise QRCodeNotFoundInDBError()

    path = qrcode.url
    os.remove(path)


async def scan_qr(qr_img: UploadFile, session: AsyncSession):
    """
    Scans a QR code image, decrypts its content, and returns the associated student.
    """

    # Validate that the uploaded file is an image
    if qr_img.content_type.split("/")[0] != "image":
        raise FileTypeNotSupportedError()

    contents = await qr_img.read()

    # Load the image from bytes using PIL
    image = Image.open(io.BytesIO(contents))

    decoded = decode(image)

    if not decoded:  # If no QR code is detected
        raise NotQRCodeError()

    # Get the data from the first QR code found and decode it to a string
    first = decoded[0].data.decode("utf-8", errors="replace")

    student_id = decrypt(first)
    student = await session.get(Student, student_id)

    if not student:  # If the student is not found in the database
        raise StudentNotFoundError()

    return student
