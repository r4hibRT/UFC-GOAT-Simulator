from src.scraper.bouts import scrape_bout_details
import traceback

url = "http://www.ufcstats.com/fight-details/701c97405da76603"
try:
    details = scrape_bout_details(url)
    printable = {k: v for k, v in details.items() if k != "soup"}
    print(printable)
except Exception as e:
    traceback.print_exc()