from ultralytics import YOLO


class CertificateDetector:

    def __init__(self, model_path):

        self.model = YOLO(model_path)

        self.class_names = {
            0: "logo",
            1: "stamp",
            2: "signature",
        }

    def detect(self, image_path):

        results = self.model.predict(
            image_path,
            conf=0.25,
            verbose=False,
        )

        output = {
            "logos": [],
            "stamps": [],
            "signatures": [],
        }

        for result in results:

            for box in result.boxes:

                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist()
                )

                item = {
                    "bbox": [
                        x1,
                        y1,
                        x2 - x1,
                        y2 - y1,
                    ],
                    "confidence": round(confidence, 4),
                }

                if cls_id == 0:
                    output["logos"].append(item)

                elif cls_id == 1:
                    output["stamps"].append(item)

                elif cls_id == 2:
                    output["signatures"].append(item)

        return output