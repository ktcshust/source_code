# send via SMTP
# email_sender.py
import boto3
import smtplib
from email.mime.text import MIMEText
from ..output_config import config

class EmailSender:

    @staticmethod
    def send_via_ses(to, subject, body):
        ses = boto3.client("ses", region_name=config.aws_region)
        ses.send_email(
            Source=config.email_sender,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": body}},
            },
        )

    @staticmethod
    def send_via_smtp(to, subject, body):
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = config.email_sender
        msg["To"] = to

        with smtplib.SMTP("localhost", 1025) as server:
            server.sendmail(config.email_sender, [to], msg.as_string())

    @staticmethod
    def send(to: str, subject: str, body: str):
        try:
            return EmailSender.send_via_ses(to, subject, body)
        except Exception:
            return EmailSender.send_via_smtp(to, subject, body)

