import re


class UdemyClassifier:

    URL_PATTERN = r"(https?://\S+|www\.\S+|ude\.my/\S+)"

    def get_center(self, box):

        xs = [p[0] for p in box]
        ys = [p[1] for p in box]

        return (
            sum(xs) / len(xs),
            sum(ys) / len(ys),
        )

    def classify(self, ocr_results):

        document = {
            "platform": "udemy",
            "certificate_title": None,
            "verification_url": None,
            "certificate_no": None,
            "student_name": None,
            "course_name": None,
            "instructor": None,
            "issue_date": None,
        }

        blocks = []

        for item in ocr_results:

            _, cy = self.get_center(
                item["box"]
            )

            blocks.append(
                {
                    "text": item["text"].strip(),
                    "y": cy,
                }
            )

        blocks.sort(
            key=lambda x: x["y"]
        )

        # ----------------------------------
        # URL
        # ----------------------------------

        for block in blocks:

            text = block["text"]

            if re.search(
                self.URL_PATTERN,
                text.lower()
            ):
                document["verification_url"] = text

        # ----------------------------------
        # Certificate Number
        # ----------------------------------

        for block in blocks:

            text = block["text"]

            if (
                "certificate no"
                in text.lower()
            ):
                document["certificate_no"] = text

        # ----------------------------------
        # Certificate Title
        # ----------------------------------

        for block in blocks:

            text = block["text"]

            if (
                "certificate of completion"
                in text.lower()
            ):
                document["certificate_title"] = text
                break

        # ----------------------------------
        # Date
        # ----------------------------------

        for block in blocks:

            text = block["text"]

            if text.lower().startswith(
                "date"
            ):
                document["issue_date"] = text

        # ----------------------------------
        # Instructor
        # ----------------------------------

        instructor_y = None

        for block in blocks:

            text = block["text"]

            if (
                "instructor"
                in text.lower()
            ):
                document["instructor"] = text
                instructor_y = block["y"]
                break

        # ----------------------------------
        # Course Name
        # Between title and instructor
        # ----------------------------------

        title_y = None

        for block in blocks:

            if (
                block["text"]
                == document["certificate_title"]
            ):
                title_y = block["y"]
                break

        course_candidates = []

        if title_y and instructor_y:

            for block in blocks:

                text = block["text"]

                if (
                    title_y < block["y"] < instructor_y
                ):

                    if len(text) > 3:

                        course_candidates.append(
                            text
                        )

        if course_candidates:

            document["course_name"] = (
                " ".join(
                    course_candidates
                )
            )

        # ----------------------------------
        # Student Name
        # Largest text after instructor
        # before date
        # ----------------------------------

        date_y = None

        for block in blocks:

            if (
                block["text"]
                == document["issue_date"]
            ):
                date_y = block["y"]
                break

        if instructor_y and date_y:

            for block in blocks:

                text = block["text"]

                if (
                    instructor_y
                    < block["y"]
                    < date_y
                ):

                    words = text.split()

                    if (
                        2 <= len(words) <= 4
                    ):

                        document[
                            "student_name"
                        ] = text
                        break

        return document