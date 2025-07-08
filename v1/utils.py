"""
Module for common helper functions used across the application.
"""

from datetime import date

from PIL import Image


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


def verif_birth_date(dob: date) -> bool:
    today = date.today()
    if dob >= today:
        return False
    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    if age < 0:
        return False
    return True


def save_image(image_file, output_path):
    """
    Save an uploaded image to the static directory in WebP format.

    Args:
        image_file: UploadFile-like object, any supported format.
        output_dir: Path to the directory where images are saved.

    Returns:
        The relative path (filename) of the saved WebP image.
    """
    try:
        # Generate a unique filename
        file_id = "Test"
        output_filename = f"{file_id}.webp"
        output_path = "static/images/" + output_filename

        # Open image and convert to RGBA for compatibility
        image = Image.open(image_file.file)
        image = image.convert("RGBA")

        # Save as WebP
        image.save(output_path, format="WEBP")
    except Exception as e:
        print(e)
