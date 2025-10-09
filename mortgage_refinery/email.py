
from email.message import EmailMessage
from email.mime.text import MIMEText
from typing import Any, Dict
import smtplib

def send_email(config: Dict[str, Any], subject: str, body: str) -> None:
    smtp_config = config.get("smtp")
    email_config = config.get("email")
    sender = smtp_config.get("username")
    recipients = email_config.get("recipients")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    with smtplib.SMTP(smtp_config.get("host"), smtp_config.get("port")) as smtp_server:
        if smtp_config.get("use_tls"):
            smtp_server.starttls()
        smtp_server.login(sender, smtp_config.get("password"))
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
