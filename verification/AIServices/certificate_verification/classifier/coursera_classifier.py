import re

from ..utils.text_cleaner import TextCleaner


class CourseraClassifier:

    URL_PATTERN = r"(https?://\S+|www\.\S+)"

    def get_center(self, box):

        xs = [p[0] for p in box]
        ys = [p[1] for p in box]

        return (
            sum(xs) / len(xs),
            sum(ys) / len(ys),
        )

    def classify(self, ocr_results):

        print("\n")
        print("=" * 60)
        print("OCR BLOCKS")
        print("=" * 60)

        for item in ocr_results:

            cx, cy = self.get_center(
                item["box"]
            )

            print(
                f"Y={int(cy):4d} | {item['text']}"
            )

        document = {
            "platform": "coursera",
            "issuer": None,
            "student_name": None,
            "course_name": None,
            "certificate_title": None,
            "verification_url": None,
        }

        # ----------------------------------
        # URL
        # ----------------------------------

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip()
            )

            if re.search(
                self.URL_PATTERN,
                text,
            ):
                document["verification_url"] = text

        # ----------------------------------
        # Issuer
        # ----------------------------------

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip()
            )

            if "coursera" in text.lower():

                document["issuer"] = "coursera"
                break

        # ----------------------------------
        # Certificate Title
        # ----------------------------------

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip().lower()
            )

            if "certificate" in text:

                document["certificate_title"] = (
                    item["text"]
                )
                break

        # ----------------------------------
        # Student Name
        # ----------------------------------

        student_candidate = None
        student_y = None

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip()
            )

            words = text.split()

            cx, cy = self.get_center(
                item["box"]
            )

            if (
                2 <= len(words) <= 5
                and text.replace(" ", "").isalpha()
            ):

                if "coursera" in text.lower():
                    continue

                if "certificate" in text.lower():
                    continue

                if len(text) > 8:

                    student_candidate = text
                    student_y = cy
                    break

        document["student_name"] = (
            student_candidate
        )

        # ----------------------------------
        # Find completed text
        # ----------------------------------

        completed_y = None

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip().lower()
            )

            if (
                "has successfully completed"
                in text
            ):

                _, completed_y = (
                    self.get_center(
                        item["box"]
                    )
                )

                break

        # ----------------------------------
        # Course Name
        # ----------------------------------

        best_course = None
        best_score = -999

        for item in ocr_results:

            text = TextCleaner.clean(
                item["text"].strip()
            )

            lower = text.lower()

            cx, cy = self.get_center(
                item["box"]
            )

            score = 0

            if any(
                keyword in lower
                for keyword in [
                    "certificate",
                    "coursera",
                    "verify",
                    "completed",
                    "offered",
                    "authorized",
                    "identity",
                    "participation",
                    "project network",
                    "subject matter expert",
                    "freedom learning group",
                ]
            ):
                continue

            if re.search(
                self.URL_PATTERN,
                text,
            ):
                continue

            if (
                document["student_name"]
                and text
                == document["student_name"]
            ):
                continue

            words = text.split()

            # ----------------------------------
            # Main Rule
            # Course appears immediately
            # after "has successfully completed"
            # ----------------------------------

            if completed_y:

                if (
                    completed_y
                    < cy
                    < completed_y + 120
                ):
                    score += 100

            # ----------------------------------
            # Good course names usually
            # have 3+ words
            # ----------------------------------

            if len(words) >= 3:
                score += 20

            # ----------------------------------
            # Long descriptions
            # ----------------------------------

            if len(words) > 8:
                score -= 40

            # ----------------------------------
            # Instructor section
            # ----------------------------------

            if cy > 550:
                score -= 50

            print(
                f"[COURSE SCORE] "
                f"{score:3d} | "
                f"Y={int(cy)} | "
                f"{text}"
            )

            if score > best_score:

                best_score = score
                best_course = text

        document["course_name"] = (
            best_course
        )

        print("\n")
        print("=" * 50)
        print("COURSERA CLASSIFIER")
        print("=" * 50)

        for key, value in document.items():

            print(
                f"{key} : {value}"
            )

        return document