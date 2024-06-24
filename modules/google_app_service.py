import os

from config import BASE_PATH
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


class GoogleApplicationService:
    def __init__(self):
        self._scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self._credential_path = os.path.join(BASE_PATH, 'secret', 'service-account.json')

    def build(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self._credential_path, self._scopes)
        service = build('sheets', 'v4', credentials=credentials)
        return service