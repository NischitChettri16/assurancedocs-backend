import requests

from playwright.sync_api import (
    sync_playwright
)

class URLVerifier:

    def __init__(self, timeout=10):
        self.timeout = timeout

    # -----------------------------------

    def verify(
        self,
        url,
        platform=None
    ):

        if platform == "udemy":

            return self._verify_udemy(
                url
            )

        return self._verify_requests(
            url
        )

    # -----------------------------------

    def _verify_requests(
        self,
        url
    ):

        try:

            response = requests.get(
                url,
                timeout=self.timeout,
                allow_redirects=True,
                headers={
                    "User-Agent":
                    "Mozilla/5.0"
                }
            )

            return {
                "valid":
                    response.status_code == 200,

                "status_code":
                    response.status_code,

                "final_url":
                    response.url,
            }

        except Exception as e:

            return {
                "valid": False,
                "status_code": None,
                "final_url": None,
                "error": str(e),
            }

    # -----------------------------------

    def _verify_udemy(
        self,
        url
    ):

        try:

            with sync_playwright() as p:

                browser = (
                    p.chromium.launch(
                        headless=True
                    )
                )

                page = (
                    browser.new_page(
                        user_agent=(
                            "Mozilla/5.0 "
                            "(Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 "
                            "(KHTML, like Gecko) "
                            "Chrome/138.0.0.0 "
                            "Safari/537.36"
                        )
                    )
                )

                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=30000
                )

                final_url = page.url

                browser.close()

            return {
                "valid": True,
                "status_code": 200,
                "final_url": final_url,
            }

        except Exception as e:

            return {
                "valid": False,
                "status_code": None,
                "final_url": None,
                "error": str(e),
            }