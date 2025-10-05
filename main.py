import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    """Fetch HTML content from a URL."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses
    return response.text


from bs4 import BeautifulSoup, Tag

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


def get_mortgage_rate(table, term: str) -> str:
    """Find the mortgage rate for a specific term in the rates table."""
    for row in table.find_all("tr", class_="co-rates_table--row"):
        rate = extract_rate_from_row(row, term)
        if rate:
            return rate
    raise ValueError(f"{term} not found in the rates table.")


def main() -> None:
    url = "https://www.onpointcu.com/home-loans/"
    html = fetch_html(url)
    table = get_rates_table(html)
    term = "30 year fixed rate"

    rate = get_mortgage_rate(table, term)
    if rate:
        try:
            rate_float = float(rate.replace('%', '').strip())
            print(f"{term}: {rate_float}%")
        except ValueError:
            print("Could not convert rate to float:", rate)
    else:
        print(f"{term} not found.")


if __name__ == "__main__":
    main()
