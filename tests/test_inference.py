import base64
from io import BytesIO
import unittest

from PIL import Image, ImageDraw
from app import app
from utilities.texts import style_template_list


def fixture_image(style=False, fmt='PNG'):
    image = Image.new('RGB', (480, 320), (35, 110, 180) if not style else (210, 150, 60))
    draw = ImageDraw.Draw(image)
    for x in range(0, 480, 24):
        draw.rectangle((x, 0, x + 11, 319), fill=((x * 7) % 256, (x * 3) % 256, 100))
    draw.ellipse((80, 55, 290, 265), fill=(230, 60, 35), outline=(250, 250, 200), width=8)
    draw.polygon([(300, 280), (400, 40), (460, 280)], fill=(30, 200, 100))
    if style:
        image = image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    buffer = BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()


def upload(style=False, fmt='PNG'):
    return BytesIO(fixture_image(style, fmt)), 'fixture.' + ('jpg' if fmt == 'JPEG' else 'png')


def decode_result(response):
    if response.status_code != 200:
        raise AssertionError(f'HTTP {response.status_code}: {response.get_data(as_text=True)[:300]}')
    payload = response.get_json()
    prefix = 'data:image/png;base64,'
    if not isinstance(payload, dict) or set(payload) != {'result', 'range_name'} or not isinstance(payload['result'], str) or not payload['result'].startswith(prefix):
        raise AssertionError('Unexpected API response contract')
    data = base64.b64decode(payload['result'][len(prefix):], validate=True)
    with Image.open(BytesIO(data)) as image:
        if image.format != 'PNG':
            raise AssertionError('Output is not PNG')
        image.verify()
    with Image.open(BytesIO(data)) as image:
        image.load()
        if image.size != (350, 233):
            raise AssertionError(f'Unexpected output dimensions: {image.size}')
        low, high = image.convert('L').getextrema()
        if low == high:
            raise AssertionError('Output is constant')
    return data


class RealInferenceTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home_renders(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Image Style Transfer', response.data)

    def test_custom_style_transfer(self):
        decode_result(self.client.post('/style-blender', data={'image_0': upload(fmt='JPEG'), 'image_1': upload(style=True)}))

    def test_all_bundled_styles(self):
        for template in style_template_list():
            with self.subTest(template=template['filename']):
                decode_result(self.client.post('/style-blender', data={'image_0': upload(), 'style_filename': template['filename']}))

    def test_cartoonization(self):
        decode_result(self.client.post('/cartoonize', data={'image_0': upload()}))

    def test_sketch_sharpness(self):
        default = decode_result(self.client.post('/pencil-sketch', data={'image_0': upload(), 'sharpen_factor': '4'}))
        sharp = decode_result(self.client.post('/pencil-sketch', data={'image_0': upload(), 'sharpen_factor': '40'}))
        with Image.open(BytesIO(default)) as a, Image.open(BytesIO(sharp)) as b:
            self.assertNotEqual(a.tobytes(), b.tobytes())
