# delivery orchestration logic
# delivery_gateway.py
from .channels.email_sender import EmailSender
from .channels.slack_sender import SlackSender
from .channels.drive_uploader import DriveUploader

class DeliveryGateway:

    @staticmethod
    def send_email(to: str, subject: str, body: str):
        return EmailSender.send(to, subject, body)

    @staticmethod
    def send_slack(message: str):
        return SlackSender.send_message(message)

    @staticmethod
    def upload_drive(file_path: str, file_name: str):
        return DriveUploader.upload(file_path, file_name)

    @staticmethod
    def deliver_report(pdf_path: str, docx_path: str):
        # Slack
        try:
            SlackSender.send_message("Báo cáo tin AI mới nhất đã có sẵn.")
        except Exception:
            pass

        # Email
        try:
            EmailSender.send(
                "you@example.com",
                "AI News Daily Report",
                "Báo cáo AI mới nhất đã sẵn sàng."
            )
        except Exception:
            pass

        # Upload Drive
        try:
            DriveUploader.upload(pdf_path, "ai_report.pdf")
        except:
            pass

