class BoxMerger:

    def __init__(
        self,
        x_gap=20,
        y_gap=15,
    ):
        self.x_gap = x_gap
        self.y_gap = y_gap

    def merge(self, candidates):

        boxes = [candidate["bbox"][:] for candidate in candidates]

        merged = True

        while merged:

            merged = False
            result = []
            used = [False] * len(boxes)

            for i in range(len(boxes)):

                if used[i]:
                    continue

                x1, y1, w1, h1 = boxes[i]

                left = x1
                top = y1
                right = x1 + w1
                bottom = y1 + h1

                used[i] = True

                changed = True

                while changed:

                    changed = False

                    for j in range(len(boxes)):

                        if used[j]:
                            continue

                        x2, y2, w2, h2 = boxes[j]

                        if self._should_merge(
                            left,
                            top,
                            right,
                            bottom,
                            x2,
                            y2,
                            x2 + w2,
                            y2 + h2,
                        ):

                            left = min(left, x2)
                            top = min(top, y2)
                            right = max(right, x2 + w2)
                            bottom = max(bottom, y2 + h2)

                            used[j] = True
                            changed = True
                            merged = True

                result.append(
                    [
                        left,
                        top,
                        right - left,
                        bottom - top,
                    ]
                )

            boxes = result

        return boxes

        

    def _should_merge(
        self,
        l1,
        t1,
        r1,
        b1,
        l2,
        t2,
        r2,
        b2,
    ):

        horizontal = (
            l1 <= r2 + self.x_gap
            and r1 + self.x_gap >= l2
        )

        vertical = (
            t1 <= b2 + self.y_gap
            and b1 + self.y_gap >= t2
        )

        return horizontal and vertical