import smtplib
from email.mime.text import MIMEText
from typing import Any, Dict, List, Optional


def send_email(
    config: Dict[str, Any], subject: str, body: str, recipients: Optional[List[str]] = None
) -> None:
    smtp_config = config["smtp"]
    sender = smtp_config["username"]
    if recipients is None:
        recipients = config["email"]["recipients"]
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    with smtplib.SMTP(smtp_config["host"], smtp_config["port"]) as smtp_server:
        if smtp_config["use_tls"]:
            smtp_server.starttls()
        smtp_server.login(sender, smtp_config["password"])
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")
