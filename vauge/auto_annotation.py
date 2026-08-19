import cv2
import os

from candidate_detector import CandidateDetector
from box_merger import BoxMerger
from dataset_manager import DatasetManager


class AnnotationTool:

    def __init__(self):

        self.detector = CandidateDetector()
        self.merger = BoxMerger()
        self.dataset = DatasetManager()

        self.image = None
        self.display = None

        self.image_path = None

        self.boxes = []

        self.selected = set()

    #######################################################

    def open(self, image_path):

        self.image_path = image_path

        self.image = cv2.imread(image_path)

        if self.image is None:
            raise FileNotFoundError(image_path)

        candidates = self.detector.detect(image_path)

        self.boxes = self.merger.merge(candidates)

        self.selected.clear()

        self.redraw()

        cv2.namedWindow("Annotation Tool")

        cv2.setMouseCallback(
            "Annotation Tool",
            self.mouse_event,
        )

        while True:

            cv2.imshow(
                "Annotation Tool",
                self.display,
            )

            key = cv2.waitKey(20) & 0xFF

            if key == ord("q"):
                break

            elif key == ord("r"):

                self.selected.clear()
                self.redraw()

            elif key == ord("s"):

                self.save_labels()

        cv2.destroyAllWindows()

    #######################################################

    def redraw(self):

        self.display = self.image.copy()

        for i, box in enumerate(self.boxes):

            x, y, w, h = box

            color = (0, 255, 0)

            if i in self.selected:
                color = (0, 0, 255)

            cv2.rectangle(
                self.display,
                (x, y),
                (x + w, y + h),
                color,
                2,
            )

            cv2.putText(
                self.display,
                str(i),
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                color,
                2,
            )

        info = (
            "Click=Select | S=Save | R=Reset | Q=Quit"
        )

        cv2.putText(
            self.display,
            info,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 0, 0),
            2,
        )

    #######################################################

    def mouse_event(
        self,
        event,
        x,
        y,
        flags,
        param,
    ):

        if event != cv2.EVENT_LBUTTONDOWN:
            return

        for idx, box in enumerate(self.boxes):

            bx, by, bw, bh = box

            if bx <= x <= bx + bw and by <= y <= by + bh:

                if idx in self.selected:

                    self.selected.remove(idx)

                else:

                    self.selected.add(idx)

                self.redraw()

                break

    #######################################################

    def save_labels(self):

        selected_boxes = []

        for idx in self.selected:

            selected_boxes.append(
                self.boxes[idx]
            )

        self.dataset.save_yolo_label(
            self.image_path,
            selected_boxes,
            class_id=0,
        )

        print()

        print("=" * 40)
        print("Saved:", os.path.basename(self.image_path))
        print("Selected:", len(selected_boxes))
        print("=" * 40)