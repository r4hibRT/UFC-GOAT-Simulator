from src.scraper.events import scrape_events
from src.scraper.bouts import scrape_bout_urls, scrape_bout_details, scrape_bout_stats
from src.scraper.fighters import scrape_fighter_profile
from src.db.insert import insert_fighter, insert_bout, insert_bout_stats, fighter_exists
from playwright.sync_api import sync_playwright
from datetime import datetime


def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%B %d, %Y").date()
    except:
        return None


def run_pipeline(events, page):
    for event in events:
        print(f"Processing event: {event['name']} ({event['date']})")
        event_date = parse_date(event["date"])
        bout_urls = scrape_bout_urls(event["url"], page)

        for bout_url in bout_urls:
            try:
                details = scrape_bout_details(bout_url, page)

                # Fighter A: skip profile scrape if already in db
                fighter_a_id = fighter_exists(details["fighter_a_url"])
                if fighter_a_id is None:
                    profile_a = scrape_fighter_profile(details["fighter_a_url"], page)
                    fighter_a_id = insert_fighter(
                        url=details["fighter_a_url"],
                        name=details["fighter_a_name"],
                        dob=profile_a["dob"],
                        height=profile_a["height"],
                        reach=profile_a["reach"],
                        stance=profile_a["stance"]
                    )

                # Fighter B — skip profile scrape if already in db
                fighter_b_id = fighter_exists(details["fighter_b_url"])
                if fighter_b_id is None:
                    profile_b = scrape_fighter_profile(details["fighter_b_url"], page)
                    fighter_b_id = insert_fighter(
                        url=details["fighter_b_url"],
                        name=details["fighter_b_name"],
                        dob=profile_b["dob"],
                        height=profile_b["height"],
                        reach=profile_b["reach"],
                        stance=profile_b["stance"]
                    )

                # Resolve winner ID
                winner_id = fighter_a_id if details["winner"] == details["fighter_a_name"] else fighter_b_id

                # Insert bout
                bout_id = insert_bout(
                    date=event_date,
                    fighter_a_id=fighter_a_id,
                    fighter_b_id=fighter_b_id,
                    winner_id=winner_id,
                    method=details["method"],
                    method_detail=details["method_detail"],
                    round_=details["round"],
                    time=details["time"],
                    weight_class=details["weight_class"],
                    is_title_fight=details["is_title_fight"],
                    is_defence=details["is_defence"]
                )

                # Scrape and insert stats
                stats = scrape_bout_stats(
                    details["soup"],
                    details["fighter_a_url"],
                    details["fighter_b_url"]
                )

                if stats:
                    insert_bout_stats(bout_id, fighter_a_id, stats[0])
                    insert_bout_stats(bout_id, fighter_b_id, stats[1])

                print(f"  ✓ {details['fighter_a_name']} vs {details['fighter_b_name']}")

            except Exception as e:
                print(f"  ✗ Failed {bout_url}: {e}")
                import traceback
                traceback.print_exc()
                continue


if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        events = scrape_events(page)
        events = list(reversed(events))
        run_pipeline(events[:1], page)

        browser.close()