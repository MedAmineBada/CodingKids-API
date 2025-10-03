"""
Module for handling QR Code generation and scanning.
"""

import base64
import hashlib
import os
import time
from os.path import exists
from random import randint

import cv2
import numpy as np
import qrcode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from fastapi import UploadFile
from pyzbar import pyzbar
from pyzbar.wrapper import ZBarSymbol
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.exceptions import (
    FileTypeNotSupportedError,
    NotQRCodeError,
    NotFoundException,
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
    while exists(path):
        filename = f"TEMP-{student_id}-{time.time()}-DP-{chr(randint(64, 64 + 26)) + str(randint(0, 999))}"
        path = f"{EnvFile.QR_CODE_SAVE_DIR}/{filename}.webp"

    img.save(path)

    # Compress the image, return its path and remove the temporary image.
    comp_qr_path = f"{EnvFile.QR_CODE_SAVE_DIR}/QR{student_id}-{time.time()}.webp"
    while exists(comp_qr_path):
        filename = f"QR{student_id}-{time.time()}-DP-{chr(randint(64, 64 + 26)) + str(randint(0, 999))}"
        comp_qr_path = f"{EnvFile.QR_CODE_SAVE_DIR}/{filename}.webp"

    compress_img(path, comp_qr_path)

    os.remove(path)
    return comp_qr_path


async def delete_qr(id: int, session: AsyncSession):
    """
    Handles deletion of a qr code
    """
    qrcode = await session.get(QRCode, id)
    if not qrcode:
        raise NotFoundException("QR Code was not found in DB.")

    path = qrcode.url
    os.remove(path)


async def scan_qr(qr_img: UploadFile, session: AsyncSession):
    """
    Scans a QR code image using advanced preprocessing and multiple detection strategies.
    Handles large images, poor contrast, and orientation issues common in phone images.
    """
    # Validate file type
    if not qr_img.content_type.startswith("image/"):
        raise FileTypeNotSupportedError()

    contents = await qr_img.read()

    # Convert to OpenCV image
    nparr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise NotQRCodeError("Invalid image data")

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Resize large images while maintaining aspect ratio
    max_size = 1600  # Higher resolution for small QR codes
    height, width = gray.shape
    if max(height, width) > max_size:
        scale = max_size / max(height, width)
        new_w = int(width * scale)
        new_h = int(height * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)

    # Preprocessing techniques
    preprocessed = [
        gray,  # Original grayscale
        cv2.GaussianBlur(gray, (5, 5), 0),  # Reduce noise
        cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        ),  # Adaptive thresholding
        cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2
        ),  # Alternative thresholding
    ]

    # Try multiple preprocessing methods
    decoded = None
    for image in preprocessed:
        decoded = pyzbar.decode(image, symbols=[ZBarSymbol.QRCODE])
        if decoded:
            break

        # Try rotated versions
        for angle in [90, 180, 270]:
            rotated = cv2.rotate(image, get_rotation_code(angle))
            decoded = pyzbar.decode(rotated, symbols=[ZBarSymbol.QRCODE])
            if decoded:
                break
        if decoded:
            break

    if not decoded:
        raise NotQRCodeError()

    # Get the first valid result
    first = decoded[0].data.decode("utf-8", errors="replace")
    student_id = decrypt(first)
    student = await session.get(Student, student_id)

    if not student:
        raise NotFoundException("This student was not found.")

    return student


def get_rotation_code(angle: int) -> int:
    """Maps angle to OpenCV rotation code"""
    return {
        90: cv2.ROTATE_90_CLOCKWISE,
        180: cv2.ROTATE_180,
        270: cv2.ROTATE_90_COUNTERCLOCKWISE,
    }[angle]
