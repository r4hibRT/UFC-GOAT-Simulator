
from bs4 import BeautifulSoup

TEST_EVENT_URL = "http://www.ufcstats.com/event-details/f354c50b8d63d9b3"

def scrape_bout_urls(event_url, page):
    page.goto(event_url, wait_until="networkidle")
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr.b-fight-details__table-row")

    bout_urls = []
    for row in rows:
        link = row.get("data-link")
        if link:
            bout_urls.append(link)

    return bout_urls
def scrape_bout_details(bout_url, page):
    page.goto(bout_url, wait_until="networkidle")
    html = page.content()
    soup = BeautifulSoup(html, "html.parser")

    # Fighter names and URLs
    fighter_tags = soup.select("a.b-link.b-fight-details__person-link")
    fighter_a_name = fighter_tags[0].get_text(strip=True)
    fighter_a_url = fighter_tags[0]["href"]
    fighter_b_name = fighter_tags[1].get_text(strip=True)
    fighter_b_url = fighter_tags[1]["href"]

    # Winner — W/L indicators
    result_tags = soup.select("i.b-fight-details__person-status")
    fighter_a_result = result_tags[0].get_text(strip=True)
    winner = fighter_a_name if fighter_a_result == "W" else fighter_b_name

    details_section = soup.select_one("div.b-fight-details__content")
    # Method
    method_container = details_section.select_one("i.b-fight-details__text-item_first")
    method = method_container.select_one("i:not([class])").get_text(strip=True)

    # Round and time
    detail_items = details_section.select("i.b-fight-details__text-item")
    round_ = detail_items[0].get_text(strip=True).replace("Round:", "").strip()
    time = detail_items[1].get_text(strip=True).replace("Time:", "").strip()

    # Title fight detection
    bout_type = soup.select_one("i.b-fight-details__fight-title")
    is_title_fight = False
    if bout_type:
        bout_text = bout_type.get_text(strip=True).lower()
        is_title_fight = "title" in bout_text

    # Method detail
    method_parts = method.split(" - ")
    method_type = method_parts[0].strip()
    method_detail = method_parts[1].strip() if len(method_parts) > 1 else None

    # Weight class
    weight_class = None
    if bout_type:
        bout_text_raw = bout_type.get_text(strip=True)
        weight_class = bout_text_raw.replace("UFC", "").replace("Title Bout", "").replace("Bout", "").strip()

    return {
        "fighter_a_name": fighter_a_name,
        "fighter_a_url": fighter_a_url,
        "fighter_b_name": fighter_b_name,
        "fighter_b_url": fighter_b_url,
        "winner": winner,
        "method": method_type,
        "method_detail": method_detail,
        "round": round_,
        "time": time,
        "weight_class": weight_class,
        "is_title_fight": is_title_fight,
        "is_defence": False,
        "soup": soup
    }


def scrape_bout_stats(soup, fighter_a_url, fighter_b_url):
    sections = soup.select("section.b-fight-details__section")

    if len(sections) < 2:
        return None

    totals_table = sections[1].select_one("table")
    if not totals_table:
        return None

    rows = totals_table.select("tr.b-fight-details__table-row")
    data_row = None
    for row in rows:
        cols = row.select("td.b-fight-details__table-col")
        if cols:
            data_row = cols
            break

    if not data_row:
        return None

    def parse_of(text):
        text = text.strip()
        if "of" in text:
            parts = text.split("of")
            return int(parts[0].strip()), int(parts[1].strip())
        return 0, 0

    def parse_control_time(text):
        text = text.strip()
        if ":" in text:
            parts = text.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        return 0

    def get_col(col, idx):
        ps = col.select("p")
        return ps[idx].get_text(strip=True) if len(ps) > idx else ""

    stats = []
    for i, fighter_url in enumerate([fighter_a_url, fighter_b_url]):
        kd = int(get_col(data_row[1], i)) if get_col(data_row[1], i).isdigit() else 0
        sig_landed, sig_attempted = parse_of(get_col(data_row[2], i))
        total_landed, total_attempted = parse_of(get_col(data_row[4], i))
        td_landed, td_attempted = parse_of(get_col(data_row[5], i))
        sub_attempts = int(get_col(data_row[7], i)) if get_col(data_row[7], i).isdigit() else 0
        control = parse_control_time(get_col(data_row[9], i))

        stats.append({
            "fighter_url": fighter_url,
            "knockdowns": kd,
            "sig_strikes_landed": sig_landed,
            "sig_strikes_attempted": sig_attempted,
            "total_strikes_landed": total_landed,
            "total_strikes_attempted": total_attempted,
            "takedowns_landed": td_landed,
            "takedowns_attempted": td_attempted,
            "submission_attempts": sub_attempts,
            "control_time_seconds": control
        })

    return stats



if __name__ == "__main__":
    test_urls = [
        "http://www.ufcstats.com/fight-details/4a0db214d9721d6e",  # Merab vs Yan 2
        "http://www.ufcstats.com/fight-details/dfa692db6d39330c",  # Pantoja vs Van
    ]
    for url in test_urls:
        details = scrape_bout_details(url)
        stats = scrape_bout_stats(
            details["soup"],
            details["fighter_a_url"],
            details["fighter_b_url"]
        )
        printable = {k: v for k, v in details.items() if k != "soup"}
        print(printable)
        print(stats)
        print()





