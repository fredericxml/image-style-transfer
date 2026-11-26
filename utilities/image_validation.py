from io import BytesIO
from pathlib import Path
from struct import error as StructError

import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError

from config import MAX_IMAGE_BYTES, MAX_IMAGE_PIXELS
from utilities.texts import style_template_list
from utilities.utils import base_path


class InvalidImage(ValueError):
    """Invalid or unsupported image input."""


def decode_image(data):
    if not data:
        raise InvalidImage('Image is empty.')
    if len(data) > MAX_IMAGE_BYTES:
        raise InvalidImage('Each image must be at most 10 MiB.')
    try:
        with Image.open(BytesIO(data)) as header:
            if header.format not in {'JPEG', 'PNG'}:
                raise InvalidImage('Only JPEG and PNG images are supported.')
            if header.width * header.height > MAX_IMAGE_PIXELS:
                raise InvalidImage('Image must contain at most 12 megapixels.')
            header.verify()
    except (UnidentifiedImageError, OSError, SyntaxError, ValueError, EOFError,
            StructError, Image.DecompressionBombError) as exc:
        if isinstance(exc, InvalidImage):
            raise
        raise InvalidImage('Invalid or unreadable JPEG/PNG image.') from exc
    try:
        image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    except cv2.error as exc:
        raise InvalidImage('Image could not be decoded.') from exc
    if image is None or not image.size:
        raise InvalidImage('Image could not be decoded.')
    return image


def style_template_path(filename):
    allowed = {entry['filename'] for entry in style_template_list()}
    if filename not in allowed:
        raise InvalidImage('Unknown style template.')
    root = Path(base_path('models', 'style_transfer', 'images')).resolve()
    path = (root / filename).resolve()
    if path.parent != root or not path.is_file():
        raise RuntimeError('Bundled style template is unavailable.')
    return path
