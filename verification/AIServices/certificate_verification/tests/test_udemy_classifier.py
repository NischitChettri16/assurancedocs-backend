from pathlib import Path
import sys


sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)
from verification.AIServices.certificate_verification.ocr.ocr_engine import OCREngine

from verification.AIServices.certificate_verification.classifier.udemy_classifier import (
    UdemyClassifier
)

IMAGE_PATH = (
    "../../datasets/test_images/"
    "udemy_0001.jpg"
)

ocr = OCREngine()

classifier = UdemyClassifier()

ocr_results = ocr.extract_text(
    IMAGE_PATH
)

result = classifier.classify(
    ocr_results
)

print()
print("=" * 50)
print("UDEMY CLASSIFIER")
print("=" * 50)

for key, value in result.items():

    print(
        f"{key} : {value}"
    )