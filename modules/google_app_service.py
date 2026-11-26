from config import GOOGLE_SERVICE_ACCOUNT_FILE


class GoogleApplicationService:
    def build(self):
        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        credentials = Credentials.from_service_account_file(
            GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=['https://www.googleapis.com/auth/spreadsheets'],
        )
        return build('sheets', 'v4', credentials=credentials, cache_discovery=False)
