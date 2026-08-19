from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.verification.page_scraper import PageScraper


url = "https://www.coursera.org/account/accomplishments/verify/1W07B1WE21PY"

scraper = PageScraper()

result = scraper.scrape(url)

print()
print("=" * 50)
print("PAGE DATA")
print("=" * 50)

print(result)