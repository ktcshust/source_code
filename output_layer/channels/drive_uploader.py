# upload to Google Drive / S3
# drive_uploader.py
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from ..output_config import config

class DriveUploader:

    @staticmethod
    def upload(file_path: str, file_name: str):
        creds = Credentials.from_service_account_file(
            config.gdrive_credentials_path,
            scopes=["https://www.googleapis.com/auth/drive"]
        )

        service = build("drive", "v3", credentials=creds)

        metadata = {"name": file_name, "parents": [config.gdrive_folder_id]}
        media = MediaFileUpload(file_path, mimetype="application/pdf")

        file = service.files().create(
            body=metadata, media_body=media, fields="id"
        ).execute()

        return file.get("id")

