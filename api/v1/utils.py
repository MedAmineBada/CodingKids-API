"""
Module for common helper functions used across the application.
"""

import io
import os
import time
from datetime import date

from PIL import Image
from PIL import Image as PILImage
from fastapi import HTTPException, UploadFile
from starlette import status

from api.v1.exceptions import StudentImageSaveError
from envconfig import EnvFile


def clean_spaces(text: str) -> str:
    stripped = text.strip()
    cleaned = " ".join(stripped.split())
    return cleaned


def verif_str(input_str: str) -> bool:
    """
    Validate that a string is non-empty and contains only alphabetic characters.
    """
    stripped = input_str.replace(" ", "")
    if not stripped:
        return False
    if not stripped.isalpha():
        return False
    return True


def verif_tel_number(input_num: str) -> bool:
    """
    Validates whether a string is a valid phone number.

    A valid phone number must:
      - Contain only digits
      - Be exactly 8 characters long
      - Not be empty
    """

    stripped = input_num.replace(" ", "")
    if not stripped:
        return False
    if not stripped.isdigit():
        return False
    if len(stripped) != 8:
        return False
    return True


def verif_cin(input_num: str) -> bool:
    """
    Validates whether a string is a valid CIN.

    A valid phone number must:
      - Contain only digits
      - Be exactly 8 characters long
      - Not be empty
    """
    stripped = input_num.replace(" ", "")
    if not stripped:
        return False
    if not stripped.isdigit():
        return False
    if len(stripped) != 8:
        return False
    return True


async def save_image(file: UploadFile, output_path: str):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type.",
        )
    try:
        image_bytes = await file.read()
        image = PILImage.open(io.BytesIO(image_bytes))

        temp_path = f"{EnvFile.STUDENT_IMAGE_SAVE_DIR}/TEMP-{time.time()}.webp"

        image.save(temp_path, format="WEBP")
        compress_img(temp_path, output_path)
        os.remove(temp_path)

    except:
        raise StudentImageSaveError()


def compress_img(src: str, dest: str):
    with Image.open(src) as img:
        img.save(
            dest,
            format="WEBP",
            lossless=True,
            quality=100,
        )


def valid_date(input_date: date) -> bool:
    today = date.today()
    if input_date >= today:
        return False
    diff = (
        today.year
        - input_date.year
        - ((today.month, today.day) < (input_date.month, input_date.day))
    )
    if diff < 0:
        return False
    return True
