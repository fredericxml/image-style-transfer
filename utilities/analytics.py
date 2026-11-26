"""Optional image storage and spreadsheet activity tracking."""
import base64
import hashlib
import logging
import re
from datetime import datetime

from itsdangerous import BadSignature, URLSafeTimedSerializer

import config
from modules.google_app_service import GoogleApplicationService

logger = logging.getLogger(__name__)
LAST_COLUMNS = {'Style Transfer': 'M', 'Cartoonize': 'H', 'Pencil Sketch': 'I'}


def enabled():
    return bool(config.ANALYTICS_ENABLED and config.IMGBB_API_KEY and
                config.SPREADSHEET_ID and len(config.TRACKING_SECRET) >= 32)


def save_image(image):
    import requests

    response = requests.post('https://api.imgbb.com/1/upload', data={
        'key': config.IMGBB_API_KEY,
        'image': base64.b64encode(image).decode('ascii'),
    }, timeout=(5, 30))
    response.raise_for_status()
    data = response.json()['data']
    return data['id'], data['url']


def write_on_google_sheet(sheet, values):
    now = datetime.now()
    row = [now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'), *values, 0]
    if sheet not in LAST_COLUMNS or len(row) != ord(LAST_COLUMNS[sheet]) - ord('A') + 1:
        raise ValueError('Invalid tracking row.')
    response = GoogleApplicationService().build().spreadsheets().values().append(
        spreadsheetId=config.SPREADSHEET_ID, range=f"'{sheet}'!A1",
        valueInputOption='RAW', insertDataOption='INSERT_ROWS', body={'values': [row]},
    ).execute(num_retries=0)
    return response['updates']['updatedRange']


def update_google_sheet(sheet, column, row, value):
    if sheet not in LAST_COLUMNS or column not in {LAST_COLUMNS[sheet], 'H' if sheet == 'Pencil Sketch' else LAST_COLUMNS[sheet]}:
        raise ValueError('Invalid tracking cell.')
    if type(row) is not int or row < 1:
        raise ValueError('Invalid tracking row.')
    return GoogleApplicationService().build().spreadsheets().values().update(
        spreadsheetId=config.SPREADSHEET_ID, range=f"'{sheet}'!{column}{row}",
        valueInputOption='RAW', body={'values': [[value]]},
    ).execute(num_retries=0)


def serializer():
    return URLSafeTimedSerializer(config.TRACKING_SECRET, salt='image-style-transfer-tracking')


def image_digest(image):
    return hashlib.sha256(image).hexdigest()


def parse_range(sheet, value):
    match = re.fullmatch(r"'?([^'!]+)'?!A([1-9]\d*):([A-Z]+)([1-9]\d*)", value)
    if not match or match[1] != sheet or match[3] != LAST_COLUMNS[sheet] or match[2] != match[4]:
        raise ValueError('Unexpected spreadsheet append range.')
    return int(match[2])


def read_token(token):
    if not enabled() or not isinstance(token, str) or len(token) > 2048:
        return None
    try:
        record = serializer().loads(token, max_age=86400)
    except BadSignature:
        return None
    if (not isinstance(record, dict) or record.get('sheet') not in LAST_COLUMNS or
            type(record.get('row')) is not int or record['row'] < 1):
        return None
    return record


def metadata(image, filename, dimension):
    image_id, link = save_image(image)
    return [image_id, link, filename, dimension, round(len(image) / 1e6, 3)]


def record_processing(sheet, image, filename, result, *, style=None, style_filename=None,
                      template=None, factor=None, previous=None):
    """Return an opaque signed row reference; failures do not block inference."""
    if not enabled():
        return None
    record = read_token(previous)
    if (sheet == 'Pencil Sketch' and record and record['sheet'] == sheet and
            record.get('digest') == image_digest(image)):
        try:
            update_google_sheet(sheet, 'H', record['row'], factor if factor is not None else -1)
        except Exception:
            logger.warning('Could not update sketch tracking.')
        return previous
    try:
        if sheet == 'Style Transfer':
            values = metadata(image, filename, result['content_dimension'])
            values += ([f'template:{template}', '', '', '', ''] if template is not None else
                       metadata(style, style_filename, result['style_dimension']))
        else:
            values = metadata(image, filename, result['dimension'])
            if sheet == 'Pencil Sketch':
                values.append(factor if factor is not None else -1)
        row = parse_range(sheet, write_on_google_sheet(sheet, values))
        return serializer().dumps({'sheet': sheet, 'row': row, 'digest': image_digest(image)})
    except Exception:
        logger.warning('Could not archive image or record processing activity.')
        return None


def record_download(token):
    record = read_token(token)
    if record is None:
        return False
    sheet = record['sheet']
    try:
        update_google_sheet(sheet, LAST_COLUMNS[sheet], record['row'], 1)
        return True
    except Exception:
        logger.warning('Could not record download activity.')
        return False
