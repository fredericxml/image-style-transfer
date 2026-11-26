from io import BytesIO
import unittest
from unittest.mock import patch

from PIL import Image
from app import app


def image_file():
    buffer = BytesIO()
    Image.new('RGB', (32, 24), 'red').save(buffer, format='PNG')
    buffer.seek(0)
    return buffer, 'sample.png'


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_missing_and_invalid_uploads(self):
        for route in ('/cartoonize', '/style-blender', '/pencil-sketch'):
            self.assertEqual(self.client.post(route).status_code, 400)
        response = self.client.post('/pencil-sketch', data={'image_0': (BytesIO(b'bad'), 'bad.png')})
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json)

    def test_file_limit(self):
        with patch('app.MAX_IMAGE_BYTES', 5):
            self.assertEqual(self.client.post('/pencil-sketch', data={'image_0': image_file()}).status_code, 413)

    def test_invalid_sharpness(self):
        for value in ('3', '41', 'abc', '5.5'):
            self.assertEqual(self.client.post('/pencil-sketch', data={'image_0': image_file(), 'sharpen_factor': value}).status_code, 400)

    def test_invalid_template(self):
        self.assertEqual(self.client.post('/style-blender', data={'image_0': image_file(), 'style_filename': '../config.py'}).status_code, 400)

    def test_sketch_success_contract(self):
        response = self.client.post('/pencil-sketch', data={'image_0': image_file(), 'sharpen_factor': '4'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json), {'result', 'range_name'})
        self.assertTrue(response.json['result'].startswith('data:image/png;base64,'))

    def test_download_endpoint_without_tracking(self):
        self.assertEqual(self.client.post('/download', json={}).json, {'tracked': False})

    def test_tracking_requires_consent(self):
        with patch('app.analytics.record_processing') as record:
            self.client.post('/pencil-sketch', data={'image_0': image_file()})
            record.assert_not_called()

    def test_tracking_opt_in(self):
        with patch('app.analytics.record_processing', return_value='signed-token') as record:
            response = self.client.post('/pencil-sketch', data={'image_0': image_file(), 'analytics_consent': 'true'})
            self.assertEqual(response.json['range_name'], 'signed-token')
            record.assert_called_once()

    def test_internal_error_does_not_leak_details(self):
        with patch('app.make_cartoon', side_effect=RuntimeError('internal details')):
            response = self.client.post('/cartoonize', data={'image_0': image_file()})
        self.assertEqual(response.status_code, 500)
        self.assertNotIn('internal details', response.json['error'])
