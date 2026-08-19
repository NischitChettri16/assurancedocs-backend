import requests
from bs4 import BeautifulSoup


class PageScraper:

    def __init__(self, timeout=10):
        self.timeout = timeout

    # -------------------------------------

    def fetch(self, url):

        try:

            response = requests.get(
                url,
                timeout=self.timeout,
                headers={
                    "User-Agent":
                    "Mozilla/5.0"
                }
            )

            if response.status_code != 200:
                return None

            return response.text

        except Exception as e:

            print("Fetch Error:", e)
            return None

    # -------------------------------------

    def scrape(self, url):

        html = self.fetch(url)

        if html is None:
            return None

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        title = ""

        if soup.title:
            title = soup.title.text.strip()

        meta_description = ""

        desc = soup.find(
            "meta",
            attrs={"name": "description"}
        )

        if desc:
            meta_description = desc.get(
                "content",
                ""
            )

        return {
            "page_title": title,
            "meta_description": meta_description,
        }