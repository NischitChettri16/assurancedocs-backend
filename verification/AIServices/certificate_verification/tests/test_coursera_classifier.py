from pathlib import Path
import sys

sys.path.append(
    str(Path(__file__).resolve().parent.parent)
)

from verification.AIServices.certificate_verification.ocr.ocr_engine import OCREngine
from verification.AIServices.certificate_verification.classifier.coursera_classifier import (
    CourseraClassifier
)

ocr = OCREngine()

classifier = CourseraClassifier()

ocr_results = ocr.extract_text(
    "../../datasets/test_images/coursera_0001.jpg"
)

result = classifier.classify(
    ocr_results
)

print()
print("=" * 50)
print("COURSERA CLASSIFIER")
print("=" * 50)

for key, value in result.items():
    print(key, ":", value)