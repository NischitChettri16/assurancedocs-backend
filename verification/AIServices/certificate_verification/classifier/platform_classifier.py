class PlatformClassifier:

    def __init__(self):

        self.coursera_keywords = [
            "coursera",
            "project certificate",
            "professional certificate",
            "coursera project network",
        ]

        self.udemy_keywords = [
            "udemy",
            "certificate of completion",
            "certificate no",
            "reference number",
        ]

    # --------------------------------------------------

    def classify(self, ocr_results):

        full_text = " ".join(
            item["text"].lower()
            for item in ocr_results
        )

        coursera_score = 0
        udemy_score = 0

        for keyword in self.coursera_keywords:

            if keyword in full_text:
                coursera_score += 1

        for keyword in self.udemy_keywords:

            if keyword in full_text:
                udemy_score += 1

        if coursera_score > udemy_score:
            return {
                "platform": "coursera",
                "confidence": round(
                    coursera_score /
                    max(
                        len(self.coursera_keywords),
                        1,
                    ),
                    2,
                ),
            }

        if udemy_score > coursera_score:
            return {
                "platform": "udemy",
                "confidence": round(
                    udemy_score /
                    max(
                        len(self.udemy_keywords),
                        1,
                    ),
                    2,
                ),
            }

        return {
            "platform": "unknown",
            "confidence": 0.0,
        }