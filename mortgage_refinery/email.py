import smtplib
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional


def send_email(
    config: Dict[str, Any], subject: str, body: str, recipients: Optional[List[str]] = None
) -> None:
    smtp_config = config.get("smtp")
    sender = smtp_config.get("username")
    if recipients is None:
        recipients = config.get("email").get("recipients")
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP(smtp_config.get("host"), smtp_config.get("port")) as smtp_server:
        if smtp_config.get("use_tls"):
            smtp_server.starttls()
        smtp_server.login(sender, smtp_config.get("password"))
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
