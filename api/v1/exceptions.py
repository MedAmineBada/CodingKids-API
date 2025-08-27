"""
Exceptions Module.

Defines custom exceptions.
"""

from fastapi import status


class AppException(Exception):
    """Base class for custom exceptions with message and HTTP status code."""

    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class StudentNotFoundError(AppException):
    def __init__(self, message="Student was not found in DB."):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class QRCodeGenerationError(AppException):
    def __init__(self, message="Failed to generate the QR Code."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRCodeDeletionError(AppException):
    def __init__(self, message="Failed to delete the QR Code."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class QRCodeNotFoundInDBError(AppException):
    def __init__(self, message="QR Code was not found in DB."):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class QRCodeNotFoundError(AppException):
    def __init__(self, message="QR Code image was not found."):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class FileTypeNotSupportedError(AppException):
    def __init__(self, message="File type is not supported."):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class QRCodeScanError(AppException):
    def __init__(self, message="QR Code scan failed."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class NotQRCodeError(AppException):
    def __init__(self, message="No QR Code was detected in image."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentImageReplaceError(AppException):
    def __init__(self, message="Failed to replace the student's image."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentImageSaveError(AppException):
    def __init__(self, message="Failed to save the student's image."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentImageDeleteError(AppException):
    def __init__(self, message="Failed to delete the student's image."):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)


class StudentImageNotFoundError(AppException):
    def __init__(self, message="Student's Image was not found in DB."):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class StudentAlreadyHasImage(AppException):
    def __init__(
        self,
        message="Student already has an image, use the appropriate route to replace it.",
    ):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)


class DateNotValid(AppException):
    def __init__(
        self,
        message="The date is not valid.",
    ):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


class AlreadyExists(AppException):
    def __init__(
        self,
        message="This resource already exists.",
    ):
        super().__init__(message, status.HTTP_409_CONFLICT)
