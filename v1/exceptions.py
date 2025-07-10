class StudentNotFound(Exception):
    pass


class QRCodeGenerationError(Exception):
    pass


class QRCodeDeletionError(Exception):
    pass


class QRCodeNotFoundInDB(Exception):
    pass


class ImageReplaceError(Exception):
    pass


class ImageSaveError(Exception):
    pass


class ImageDeleteError(Exception):
    pass


class ImageNotFoundError(Exception):
    pass
