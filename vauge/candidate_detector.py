import cv2
import numpy as np


class CandidateDetector:

    def __init__(
        self,
        min_width=15,
        min_height=8,
        max_width_ratio=0.95,
        max_height_ratio=0.70,
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.max_width_ratio = max_width_ratio
        self.max_height_ratio = max_height_ratio

    def detect(self, image_path):

        image = cv2.imread(image_path)

        if image is None:
            raise FileNotFoundError(image_path)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # ----------------------------------------
        # Adaptive Threshold
        # ----------------------------------------
        binary = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            31,
            8,
        )

        # ----------------------------------------
        # Edge Detection
        # ----------------------------------------
        edges = cv2.Canny(
            gray,
            60,
            150,
        )

        # ----------------------------------------
        # Combine
        # ----------------------------------------
        combined = cv2.bitwise_or(binary, edges)

        # ----------------------------------------
        # Morphological Close
        # ----------------------------------------
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (3, 3),
        )

        combined = cv2.morphologyEx(
            combined,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=2,
        )

        # ----------------------------------------
        # Save debug image
        # ----------------------------------------
        cv2.imwrite("combined_mask.jpg", combined)

        # ----------------------------------------
        # Find contours
        # ----------------------------------------
        contours, hierarchy = cv2.findContours(
            combined,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        print(f"Total contours found: {len(contours)}")

        h, w = image.shape[:2]

        candidates = []

        for contour in contours:

            x, y, bw, bh = cv2.boundingRect(contour)

            # ------------------------
            # Filter tiny noise
            # ------------------------
            if bw < self.min_width:
                continue

            if bh < self.min_height:
                continue

            # ------------------------
            # Ignore huge regions
            # ------------------------
            if bw > w * self.max_width_ratio:
                continue

            if bh > h * self.max_height_ratio:
                continue

            area = bw * bh

            candidates.append(
                {
                    "bbox": [x, y, bw, bh],
                    "area": area,
                }
            )

        print(f"Candidates after filtering: {len(candidates)}")

        return image, combined, candidates

    def visualize(self, image, candidates):

        output = image.copy()

        for idx, candidate in enumerate(candidates):

            x, y, w, h = candidate["bbox"]

            cv2.rectangle(
                output,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                output,
                str(idx),
                (x, y - 3),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )

        return output