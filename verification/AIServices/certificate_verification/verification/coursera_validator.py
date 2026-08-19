import re

from .page_scraper import PageScraper


class CourseraValidator:

    def __init__(self):
        self.scraper = PageScraper()

    # -----------------------------------

    def validate(self, url):

        page_data = self.scraper.scrape(url)

        if page_data is None:
            return None

        description = page_data.get(
            "meta_description",
            ""
        )

        course_name = None

        match = re.search(
            r'"([^"]+)"',
            description
        )

        if match:
            course_name = match.group(1)

        return {
            "platform": "coursera",
            "course_name": course_name,
            "page_title": page_data["page_title"],
        }