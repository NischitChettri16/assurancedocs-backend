from pathlib import Path
import shutil
import cv2


class DatasetManager:

    SUPPORTED_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".webp",
    }

    def __init__(self, image_directory):

        self.image_directory = Path(image_directory)

        if not self.image_directory.exists():
            raise FileNotFoundError(
                f"Directory not found: {self.image_directory}"
            )

        self.images = self._load_images()
        self.index = 0

    ############################################################
    # Image Navigation
    ############################################################

    def _load_images(self):

        images = []

        for ext in self.SUPPORTED_EXTENSIONS:
            images.extend(self.image_directory.glob(f"*{ext}"))
            images.extend(self.image_directory.glob(f"*{ext.upper()}"))

        return sorted(images)

    def current(self):

        if not self.images:
            return None

        return self.images[self.index]

    def next(self):

        if self.has_next():
            self.index += 1

        return self.current()

    def previous(self):

        if self.has_previous():
            self.index -= 1

        return self.current()

    def first(self):

        self.index = 0
        return self.current()

    def last(self):

        if self.images:
            self.index = len(self.images) - 1

        return self.current()

    def goto(self, index):

        if 0 <= index < len(self.images):
            self.index = index

        return self.current()

    def total_images(self):

        return len(self.images)

    def current_index(self):

        return self.index

    def has_next(self):

        return self.index < len(self.images) - 1

    def has_previous(self):

        return self.index > 0

    def image_name(self):

        image = self.current()

        return image.name if image else None

    def image_stem(self):

        image = self.current()

        return image.stem if image else None

    def progress(self):

        if not self.images:
            return "0 / 0"

        return f"{self.index + 1} / {len(self.images)}"

    ############################################################
    # YOLO Dataset Writer
    ############################################################

    def save_yolo_label(
        self,
        image_path,
        boxes,
        class_id=0,
        output_root="dataset",
    ):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(image_path)

        images_dir = Path(output_root) / "images" / "train"
        labels_dir = Path(output_root) / "labels" / "train"

        images_dir.mkdir(parents=True, exist_ok=True)
        labels_dir.mkdir(parents=True, exist_ok=True)

        # Copy image only if it isn't already there
        destination = images_dir / image_path.name

        if not destination.exists():
            shutil.copy(image_path, destination)

        image = cv2.imread(str(image_path))

        if image is None:
            raise RuntimeError(f"Cannot read image: {image_path}")

        height, width = image.shape[:2]

        label_path = labels_dir / f"{image_path.stem}.txt"

        with open(label_path, "w") as f:

            for x, y, w, h in boxes:

                x_center = (x + w / 2) / width
                y_center = (y + h / 2) / height

                w_norm = w / width
                h_norm = h / height

                f.write(
                    f"{class_id} "
                    f"{x_center:.6f} "
                    f"{y_center:.6f} "
                    f"{w_norm:.6f} "
                    f"{h_norm:.6f}\n"
                )

        print(f"[✓] Saved image : {destination}")
        print(f"[✓] Saved label : {label_path}")