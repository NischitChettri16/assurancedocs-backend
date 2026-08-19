

import cv2
import os

from verification.AIServices.certificate_verification.annotation.dataset_manager import DatasetManager


class AnnotationTool:

    def __init__(self, image_directory):

        self.dataset = DatasetManager(image_directory)

        self.image = None
        self.display = None
        self.image_path = None

        self.boxes = []

        self.drawing = False

        self.start_x = 0
        self.start_y = 0

    #######################################################

    def open(self):

        self.load_current_image()

        cv2.namedWindow(
            "Annotation Tool",
            cv2.WINDOW_NORMAL,
        )

        cv2.resizeWindow(
            "Annotation Tool",
            1400,
            900,
        )

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
                self.boxes.clear()
                self.redraw()

            elif key == ord("u"):  # Undo
                if self.boxes:
                    self.boxes.pop()
                self.redraw()

            elif key == ord("s"):

                self.save_labels()

                if self.dataset.has_next():
                    self.dataset.next()
                    self.load_current_image()

            elif key == ord("n"):

                if self.dataset.has_next():
                    self.dataset.next()
                    self.load_current_image()

            elif key == ord("p"):

                if self.dataset.has_previous():
                    self.dataset.previous()
                    self.load_current_image()

        cv2.destroyAllWindows()

    #######################################################

    def load_current_image(self):

        image_path = self.dataset.current()

        if image_path is None:
            return

        self.image_path = str(image_path)

        self.image = cv2.imread(self.image_path)

        if self.image is None:
            raise FileNotFoundError(self.image_path)

        self.boxes.clear()

        self.redraw()

    #######################################################

    def redraw(self):

        self.display = self.image.copy()

        for i, (x, y, w, h) in enumerate(self.boxes):

            cv2.rectangle(
                self.display,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2,
            )

            cv2.putText(
                self.display,
                str(i),
                (x, y - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 0),
                2,
            )

        info = (
            f"{self.dataset.progress()} | "
            f"{self.dataset.image_name()} | "
            "Drag=Draw "
            "S=Save "
            "U=Undo "
            "R=Reset "
            "N=Next "
            "P=Previous "
            "Q=Quit"
        )

        cv2.putText(
            self.display,
            info,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
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

        if event == cv2.EVENT_LBUTTONDOWN:

            self.drawing = True

            self.start_x = x
            self.start_y = y

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:

            temp = self.image.copy()

            for bx, by, bw, bh in self.boxes:

                cv2.rectangle(
                    temp,
                    (bx, by),
                    (bx + bw, by + bh),
                    (0, 255, 0),
                    2,
                )

            cv2.rectangle(
                temp,
                (self.start_x, self.start_y),
                (x, y),
                (0, 0, 255),
                2,
            )

            self.display = temp

        elif event == cv2.EVENT_LBUTTONUP:

            self.drawing = False

            x1 = min(self.start_x, x)
            y1 = min(self.start_y, y)

            w = abs(x - self.start_x)
            h = abs(y - self.start_y)

            if w > 5 and h > 5:

                self.boxes.append(
                    [x1, y1, w, h]
                )

            self.redraw()

    #######################################################

    def save_labels(self):

        self.dataset.save_yolo_label(
            image_path=self.image_path,
            boxes=self.boxes,
            class_id=0,
            output_root="../datasets",
        )

        print()
        print("=" * 50)
        print("Saved:", os.path.basename(self.image_path))
        print("Boxes:", len(self.boxes))
        print("=" * 50)