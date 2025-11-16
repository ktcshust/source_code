# send via SMTP or save to S3
import aiosmtplib, os
from email.message import EmailMessage
from app.config import settings

async def send_report_via_smtp(to_email: str, subject: str, body: str, attachments: list[str]=None):
    msg = EmailMessage()
    msg["From"] = settings.SMTP_USER or "noreply@example.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)
    # attach files
    for p in attachments or []:
        with open(p, "rb") as f:
            data = f.read()
        maintype = "application"
        subtype = "octet-stream"
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=os.path.basename(p))
    await aiosmtplib.send(msg, hostname=settings.SMTP_HOST, port=settings.SMTP_PORT, username=settings.SMTP_USER, password=settings.SMTP_PASSWORD, start_tls=True)

