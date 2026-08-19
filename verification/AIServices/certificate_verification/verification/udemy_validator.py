from playwright.sync_api import (
    sync_playwright
)

from bs4 import BeautifulSoup


import re



class UdemyValidator:
    
    def extract_course_name(
    self,
    meta_description
    ):

     match = re.search(
         r'certificate for "(.*?)"',
         meta_description
     )

     if match:
         return match.group(1)
 
     return None
 
    def validate(self, url):

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
                            "(Windows NT 10.0; "
                            "Win64; x64) "
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

                html = page.content()

                final_url = page.url

                browser.close()

            soup = BeautifulSoup(
                html,
                "html.parser"
            )

            page_title = ""

            if soup.title:
                page_title = (
                    soup.title.text.strip()
                )

            meta_description = ""

            meta = soup.find(
                "meta",
                attrs={
                    "name": "description"
                }
            )

            if meta:
                meta_description = (
                    meta.get(
                        "content",
                        ""
                    )
                )
            course_name=self.extract_course_name(
                meta_description
            )

            return {
                "page_title":
                    page_title,

                "meta_description":
                    meta_description,
                "course_name":course_name, 
                "final_url":
                    final_url,
            }

        except Exception as e:

            print(
                f"Udemy validation error: {e}"
            )

            return None