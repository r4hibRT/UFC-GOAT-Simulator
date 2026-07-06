from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

EVENTS_URL = "http://www.ufcstats.com/statistics/events/completed?page=all"

def scrape_events():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(EVENTS_URL, wait_until="networkidle")

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr.b-statistics__table-row")

    events = []
    for row in rows:
        name_tag = row.select_one("a.b-link")
        date_tag = row.select_one("span.b-statistics__date")

        if not name_tag or not date_tag:
            continue

        events.append({
            "name": name_tag.get_text(strip=True),
            "date": date_tag.get_text(strip=True),
            "url": name_tag["href"]
        })

    return events

if __name__ == "__main__":
    events = scrape_events()
    print(f"Found {len(events)} events")
    print(events[0])