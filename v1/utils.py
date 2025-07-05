"""
Module for common helper functions used across the application.
"""


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
