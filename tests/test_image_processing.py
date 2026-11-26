import base64
from io import BytesIO
import unittest
from unittest.mock import patch

import cv2
import numpy as np
from PIL import Image

from modules.pencil_sketch import dodge, make_sketch
from utilities.image_validation import InvalidImage, decode_image, style_template_path
from utilities.texts import style_template_list
from utilities.utils import optimize_image_size


def sample_image(fmt='PNG', size=(600, 100), mode='RGB'):
    buffer = BytesIO()
    Image.new(mode, size, 0).save(buffer, format=fmt)
    return buffer.getvalue()


class ImageValidationTests(unittest.TestCase):
    def test_valid_jpeg_png(self):
        for fmt in ('JPEG', 'PNG'):
            self.assertEqual(decode_image(sample_image(fmt)).shape, (100, 600, 3))

    def test_grayscale_and_rgba(self):
        for mode in ('L', 'RGBA'):
            self.assertEqual(decode_image(sample_image(mode=mode)).shape, (100, 600, 3))

    def test_invalid_images(self):
        for data in (b'', b'not an image', sample_image('GIF'), sample_image()[:32]):
            with self.assertRaises(InvalidImage):
                decode_image(data)

    def test_byte_limit(self):
        with patch('utilities.image_validation.MAX_IMAGE_BYTES', 10):
            with self.assertRaises(InvalidImage):
                decode_image(sample_image())

    def test_pixel_limit(self):
        with patch('utilities.image_validation.MAX_IMAGE_PIXELS', 10):
            with patch('utilities.image_validation.cv2.imdecode') as decoder:
                with self.assertRaises(InvalidImage):
                    decode_image(sample_image())
                decoder.assert_not_called()

    def test_template_allowlist(self):
        for entry in style_template_list():
            path = style_template_path(entry['filename'])
            self.assertEqual(path.name, entry['filename'])
            self.assertEqual(decode_image(path.read_bytes()).shape[-1], 3)
        for name in ('../config.py', '/etc/passwd', 'unknown.jpg', ''):
            with self.assertRaises(InvalidImage):
                style_template_path(name)


class SketchTests(unittest.TestCase):
    def test_extreme_aspect_ratios(self):
        self.assertEqual(optimize_image_size((1, 10000)), [1, 350])
        self.assertEqual(optimize_image_size((10000, 1)), [350, 1])

    def test_dodge_zero_denominator(self):
        with np.errstate(divide='raise', invalid='raise'):
            result = dodge(np.array([[255]], dtype=np.uint8), np.array([[0]], dtype=np.uint8))
        self.assertEqual(result.item(), 255)

    def test_sketch_outputs(self):
        for size, shape in [((600, 100), (58, 350)), ((100, 600), (350, 58)), ((100, 100), (100, 100)), ((600, 1), (1, 350))]:
            for factor in (None, 5, 40):
                with self.subTest(size=size, factor=factor):
                    result = make_sketch(sample_image(size=size), factor)['image']
                    raw = base64.b64decode(result.split(',', 1)[1], validate=True)
                    image = cv2.imdecode(np.frombuffer(raw, np.uint8), cv2.IMREAD_GRAYSCALE)
                    self.assertEqual(image.shape, shape)
