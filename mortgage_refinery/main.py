import logging
import time

import requests
from bs4 import BeautifulSoup, Tag

from mortgage_refinery.config import load_config
from mortgage_refinery.email import send_email
from mortgage_refinery.rate_tracker import RateTracker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


CHECK_INTERVAL_SECONDS = 300
TERM = "30 year fixed rate"
URL = "https://www.onpointcu.com/home-loans/"
    

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
            return float(rate.replace("%", "").strip())
    raise ValueError(f"{term} not found in the rates table.")


def check_and_notify(config, tracker) -> None:
    """Check the current rate and send notification if conditions are met."""
    threshold = config.get("threshold")

    try:
        html = fetch_html(URL)
        table = get_rates_table(html)
        current_rate = get_mortgage_rate(table, TERM)

        logger.info(f"Current {TERM}: {current_rate}% (threshold: {threshold}%)")

        tracker.record_check(current_rate)

        if tracker.should_send_alert(current_rate, threshold):
            send_email(
                config,
                subject=f"Mortgage Rate Alert: {TERM} now {current_rate}%",
                body=(
                    f"Great news! The {TERM} has dropped to {current_rate}%.\n\n"
                    f"This is below your threshold of {threshold}%.\n"
                    f"Previous alert was for: {tracker.history.last_alerted_rate}%.\n\n"
                    f"It might be time to refinance!\n\n"
                    f"---\n"
                    f"{tracker.get_summary()}"
                ),
            )
            tracker.record_alert(current_rate)
            logger.info("Alert sent successfully.")
        else:
            logger.info("No alert sent (conditions not met).")

    except Exception as e:
        logger.error(f"Error checking reatges: {e}", exc_info=True)


def main() -> None:
    """Main entry point - run continuously with periodic checks."""
    logger.info(f"Starting mortgage rate monitor (checking every {CHECK_INTERVAL_SECONDS}s)")
    logger.info(f"Monitoring: {TERM} at {URL}")

    try:
        config = load_config()
        logger.info(f"Alert theshold: {config.get('threshold')}%")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return

    tracker = RateTracker()
    logger.info(f"Current tracking state:\n{tracker.get_summary()}")

    while True:
        try:
            check_and_notify(config, tracker)
        except KeyboardInterrupt:
            logger.info("Shutting down gracefully...")
            break
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)

        logger.info(f"Next check in {CHECK_INTERVAL_SECONDS} seconds...")
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()
