import os

from dotenv import load_dotenv

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_PATH, ".env"), override=False)
HOST = os.getenv('APP_HOST', '127.0.0.1')
PORT = int(os.getenv('APP_PORT', '5000'))
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_IMAGE_PIXELS = 12_000_000
MAX_REQUEST_BYTES = 21 * 1024 * 1024

# External storage and spreadsheet tracking require explicit configuration.
ANALYTICS_ENABLED = os.getenv('ANALYTICS_ENABLED', 'false').lower() in {'1', 'true', 'yes'}
IMGBB_API_KEY = os.getenv('IMGBB_API_KEY', '')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID', '')
GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv(
    'GOOGLE_SERVICE_ACCOUNT_FILE', os.path.join(BASE_PATH, 'secret', 'service-account.json'))
if not os.path.isabs(GOOGLE_SERVICE_ACCOUNT_FILE):
    GOOGLE_SERVICE_ACCOUNT_FILE = os.path.join(BASE_PATH, GOOGLE_SERVICE_ACCOUNT_FILE)
TRACKING_SECRET = os.getenv('TRACKING_SECRET', '')
