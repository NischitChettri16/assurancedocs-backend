import re

class URLExtractor:

    URL_PATTERNS = [
        r"(https?://[^\s]+)",
        r"(www\.[^\s]+)",
        r"(ude\.my/[A-Za-z0-9\-_]+)",
        r"(coursera\.org/verify/[A-Za-z0-9\-_]+)",
    ]

    def extract(self, ocr_results):

        urls = []

        for item in ocr_results:

            text = item["text"]

            for pattern in self.URL_PATTERNS:

                matches = re.findall(
                    pattern,
                    text,
                    re.IGNORECASE,
                )

                for match in matches:

                    url = match.strip()

                    if url.startswith("www."):
                        url = f"https://{url}"

                    elif url.startswith("ude.my"):
                        url = f"https://{url}"

                    elif url.startswith("coursera.org"):
                        url = f"https://{url}"

                    urls.append(
                        {
                            "url": url,
                            "source": item,
                        }
                    )

        return urls

    def get_primary_url(self, ocr_results):

        urls = self.extract(
            ocr_results
        )

        if not urls:
            return None

        return urls[0]