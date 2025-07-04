import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers import (
    RoundedModuleDrawer,
)


def gen():
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.ERROR_CORRECT_H,
        box_size=16,
        border=1,
        image_factory=StyledPilImage,
        mask_pattern=None,
    )
    qr.add_data("Hello World")
    qr.make(fit=True)
    img = qr.make_image(
        color_mask=SolidFillColorMask(
            front_color=(244, 180, 46),
            back_color=(255, 255, 255),
        ),
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path="static/ck_logo.png",
    )
    img.save(f"static/QRCodes/example.png")
