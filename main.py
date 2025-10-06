import requests
from bs4 import BeautifulSoup
import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup, Tag
import yaml


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_html(url: str) -> str:
    """Fetch HTML content from a URL."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text


def get_rates_table(html: str) -> Tag:
    """Parse HTML and return the rates table."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="co-rates_table")
    if not table:
        raise ValueError("Rates table not found in the HTML.")
    return table


def extract_rate_from_row(row, term: str) -> str | None:
    """Return the rate percentage from a row if the term matches, else None."""
    cells = row.find_all("td")
    if cells and term in cells[0].get_text(strip=True).lower():
        p_tags = cells[1].find_all("p")
        for p in p_tags:
            text = p.get_text(strip=True)
            if text.endswith("%"):
                return text
    return None


def get_mortgage_rate(table, term: str) -> float:
    """Find the mortgage rate for a specific term in the rates table."""
    for row in table.find_all("tr", class_="co-rates_table--row"):
        rate = extract_rate_from_row(row, term)
        if rate:
            return float(rate.replace('%', '').strip())
    raise ValueError(f"{term} not found in the rates table.")


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml if it exists."""
    config_path = Path("config.yaml")
    if config_path.exists():
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    raise ValueError("config.yaml not found.")


def send_email(config: Dict[str, Any], subject: str, body: str) -> None:
    smtp_config = config.get("smtp")
    email_config = config.get("email")
    sender = email_config.get("from")
    recipients = email_config.get("to")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    with smtplib.SMTP_SSL(smtp_config.get("host"), smtp_config.get("port")) as smtp_server:
       smtp_server.login(smtp_config.get("username"), smtp_config.get("password"))
       smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Message sent!")


def main() -> None:
    url = "https://www.onpointcu.com/home-loans/"
    html = fetch_html(url)
    table = get_rates_table(html)
    term = "30 year fixed rate"

    config = load_config()
    rate = get_mortgage_rate(table, term)
    threshold = config.get("threshold")
    if rate < threshold:
        send_email(
            config,
            subject="OnPoint Mortgage Rate Alert",
            body=f"{term} is now {rate}%, which is below your threshold of {threshold}%.",
        )

if __name__ == "__main__":
    main()
