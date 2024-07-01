import os
import base64

import cv2
import requests
from config import BASE_PATH
from datetime import datetime
from modules.google_app_service import GoogleApplicationService


google_sheet = GoogleApplicationService().build().spreadsheets()


def base_path(*args):
    return os.path.join(BASE_PATH, *args)


def base64_uri_from_array(image_array):
    base64_string = base64.b64encode(cv2.imencode('.png', image_array)[1]).decode()
    base64_uri = f'data:image/png;base64,{base64_string}'
    return base64_uri


def write_on_google_sheet(feature_sheet, data={}):
    # Don't write anything on development environment
    if os.getenv('MODE') == 'development':
        return None
    
    range_name = f'{feature_sheet}!A1:A1'

    values = [
        datetime.now().strftime('%Y-%m-%d'), # date
        datetime.now().strftime('%H:%M:%S')  # time
    ]
    values.extend(data.values())
    values.append(0) # Last column is download, 0 means not downloaded yet
    body = {'values': [values]}

    try:
        result = google_sheet.values().append(
            range=range_name,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            spreadsheetId=os.getenv('SPREADSHEET_ID'),
            body=body
        ).execute()
        return result['updates']['updatedRange']
    except Exception as e:
        return {'error': str(e)}, 500
    

def update_google_sheet(range_name, values):
    # Don't update anything on development environment
    if os.getenv('MODE') == 'development':
        return None
    
    values = values # Must be a list representing data in a row
    body = {'values': [values]}

    try:
        result = google_sheet.values().update(
            range=range_name,
            valueInputOption='RAW',
            spreadsheetId=os.getenv('SPREADSHEET_ID'),
            body=body
        ).execute()
        return result
    except Exception as e:
        return {'error': str(e)}, 500


def save_image(image):
    # Don't save image on development environment
    if os.getenv('MODE') == 'development':
        return None, None
    
    response = requests.post('https://api.imgbb.com/1/upload', data={
        'key': os.getenv('IMGBB_API_KEY'),
        'image': base64.b64encode(image)
    }).json()
    return response['data']['id'], response['data']['url']