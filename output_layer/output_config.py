# config for output layer
from pydantic import BaseModel
import os

class OutputConfig(BaseModel):
    email_sender: str = os.getenv("EMAIL_SENDER", "noreply@example.com")
    aws_region: str = os.getenv("AWS_REGION", "ap-southeast-1")

    slack_bot_token: str = os.getenv("SLACK_BOT_TOKEN", "")
    slack_channel: str = os.getenv("SLACK_CHANNEL", "#general")

    gdrive_credentials_path: str = os.getenv("GDRIVE_CREDENTIALS", "credentials.json")
    gdrive_folder_id: str = os.getenv("GDRIVE_FOLDER_ID", "")

    output_dir: str = os.getenv("OUTPUT_DIR", "outputs")


config = OutputConfig()

