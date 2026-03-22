import logging
import os
import sys
from datetime import timedelta, datetime, UTC
from pathlib import Path


from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from config import GOOGLE_FOLDER_ID, GOOGLE_CREDENTIALS_PATH, GOOGLE_TOKEN_PATH, SCRIPT_DIR

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

class DriveRunner:

    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self):
        self.google_credentials_path = Path(SCRIPT_DIR, GOOGLE_CREDENTIALS_PATH)
        self.google_token_path = Path(SCRIPT_DIR, GOOGLE_TOKEN_PATH)
        self.service = build("drive", "v3", credentials=self._get_credentials())

    def _get_credentials(self) -> service_account.Credentials:
        """Loads the credentials from token.json or requires login if not present in solution"""
        credentials = None
        if os.path.exists(self.google_token_path):
            credentials = Credentials.from_authorized_user_file(self.google_token_path, scopes=self.SCOPES)

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.google_credentials_path,
                    scopes=self.SCOPES
                )
                credentials = flow.run_local_server(port=0)

            with open(self.google_token_path, "w") as f:
                f.write(credentials.to_json())

        return credentials

    def upload_folder(self, folder_path: Path) -> str:
        """Uploads a folder and its contents, returns the share link"""

        folder_name = os.path.basename(folder_path)

        folder_id = self._create_drive_folder(folder_name)

        for file in os.listdir(folder_path):

            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                self._upload_file(file_path, folder_id)

        self._make_sharable(folder_id)
        link = f"https://drive.google.com/drive/folders/{folder_id}"
        logging.info(f"Uploaded folder link: {link}")

        return link

    def cleanup_old_folders(self, days_old: int=3) -> None:
        """Delete old folders inside the Game_Highlights folder"""

        cutoff = datetime.now(UTC) - timedelta(days=days_old)
        query = f"'{GOOGLE_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'"

        results = self.service.files().list(
            q=query,
            fields="files(id, name, createdTime)"
        ).execute()

        for folder in results.get('files', []):
            created = datetime.fromisoformat(folder['createdTime'].replace('Z', ''))
            if created < cutoff:
                self.service.files().delete(fileId=folder['id']).execute()
                logging.info(f"Deleted folder: {folder['name']}")

    def _create_drive_folder(self, folder_name: str) -> str:
        """Creates a folder inside the Game_Highlights folder then returns the id"""

        md = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [GOOGLE_FOLDER_ID]
        }

        folder = self.service.files().create(body=md, fields='id').execute()
        return folder['id']

    def _upload_file(self, file_path: str, parent_folder_id: str) -> None:
        """Uploads a singular file"""

        md = {
            'name': os.path.basename(file_path),
            'parents': [parent_folder_id]
        }

        media = MediaFileUpload(file_path, resumable=True)
        self.service.files().create(body=md, media_body=media).execute()

        logging.info(f"Uploaded file: {os.path.basename(file_path)}")

    def _make_sharable(self, folder_id: str) -> None:
        """Makes a singular folder viewable by anyone with the link"""

        self.service.permissions().create(
            fileId=folder_id,
            body={
                'type': 'anyone',
                'role': 'reader',
            }
        ).execute()