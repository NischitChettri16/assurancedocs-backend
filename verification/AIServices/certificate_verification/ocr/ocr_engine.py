from pathlib import Path


class OCREngine:

    def __init__(self, lang="en"):

        from paddleocr import PaddleOCR
        self.ocr = PaddleOCR(
            use_angle_cls=True,
            lang=lang,
        )

    # --------------------------------------------------

    def extract_text(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        result = self.ocr.ocr(
            str(image_path)
        )

        extracted = []

        if not result:
            return extracted

        page = result[0]

        texts = page.get("rec_texts", [])
        scores = page.get("rec_scores", [])
        boxes = page.get("dt_polys", [])

        for text, score, box in zip(
            texts,
            scores,
            boxes,
        ):

            points = (
                box.tolist()
                if hasattr(box, "tolist")
                else box
            )

            points = [
                [int(x), int(y)]
                for x, y in points
            ]

            extracted.append(
                {
                    "text": text.strip(),
                    "confidence": round(
                        float(score),
                        4,
                    ),
                    "box": points,
                }
            )

        return extracted

    # --------------------------------------------------

    def extract_plain_text(self, image_path):

        results = self.extract_text(
            image_path
        )

        return "\n".join(
            item["text"]
            for item in results
        )

    # --------------------------------------------------

    def extract_lower_text(self, image_path):

        return self.extract_plain_text(
            image_path
        ).lower()