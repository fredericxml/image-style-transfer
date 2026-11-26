import unittest
from unittest.mock import patch

from utilities import analytics


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        settings = patch.multiple(analytics.config, ANALYTICS_ENABLED=True,
                                  IMGBB_API_KEY='test', SPREADSHEET_ID='test',
                                  TRACKING_SECRET='test-secret-for-unit-tests-only-123456')
        settings.start()
        self.addCleanup(settings.stop)
        self.image = b'synthetic input'

    def test_disabled_does_not_upload(self):
        with patch.object(analytics.config, 'ANALYTICS_ENABLED', False), patch.object(analytics, 'save_image') as upload:
            self.assertIsNone(analytics.record_processing('Cartoonize', self.image, 'test.png', {'dimension': '24x32'}))
            upload.assert_not_called()

    def test_custom_and_template_style_rows(self):
        for template in (None, 'Starry Night.jpg'):
            with self.subTest(template=template), patch.object(analytics, 'save_image', return_value=('id', 'link')) as upload, patch.object(analytics, 'write_on_google_sheet', return_value="'Style Transfer'!A5:M5") as append:
                token = analytics.record_processing('Style Transfer', self.image, 'main.png', {'content_dimension': '24x32', 'style_dimension': '40x50'}, style=b'style', style_filename='style.png', template=template)
                self.assertEqual(analytics.read_token(token)['row'], 5)
                self.assertEqual(len(append.call_args.args[1]), 10)
                self.assertEqual(upload.call_count, 1 if template else 2)

    def test_cartoonization_and_download(self):
        with patch.object(analytics, 'save_image', return_value=('id', 'link')), patch.object(analytics, 'write_on_google_sheet', return_value='Cartoonize!A6:H6'), patch.object(analytics, 'update_google_sheet') as update:
            token = analytics.record_processing('Cartoonize', self.image, 'main.png', {'dimension': '24x32'})
            self.assertTrue(analytics.record_download(token))
            update.assert_called_once_with('Cartoonize', 'H', 6, 1)

    def test_sketch_adjustment_reuses_row(self):
        with patch.object(analytics, 'save_image', return_value=('id', 'link')) as upload, patch.object(analytics, 'write_on_google_sheet', return_value="'Pencil Sketch'!A7:I7") as append, patch.object(analytics, 'update_google_sheet') as update:
            result = {'dimension': '24x32'}
            token = analytics.record_processing('Pencil Sketch', self.image, 'main.png', result)
            self.assertEqual(analytics.record_processing('Pencil Sketch', self.image, 'main.png', result, factor=20, previous=token), token)
            upload.assert_called_once()
            append.assert_called_once()
            update.assert_called_once_with('Pencil Sketch', 'H', 7, 20)
            self.assertTrue(analytics.record_download(token))
            update.assert_called_with('Pencil Sketch', 'I', 7, 1)

    def test_arbitrary_range_cannot_update_sheet(self):
        with patch.object(analytics, 'update_google_sheet') as update:
            self.assertFalse(analytics.record_download('Cartoonize!A1:H1'))
            update.assert_not_called()

    def test_service_failure_does_not_break_processing(self):
        with patch.object(analytics, 'save_image', side_effect=RuntimeError('network')):
            self.assertIsNone(analytics.record_processing('Cartoonize', self.image, 'main.png', {'dimension': '24x32'}))
