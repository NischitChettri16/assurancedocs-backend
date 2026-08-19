from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.ocr.ocr_engine import OCREngine


IMAGE_PATH = "../../datasets/test_images/udemy_0001.jpg"

ocr = OCREngine()

results = ocr.extract_text(
    IMAGE_PATH
)

print()
print("=" * 60)
print("OCR RESULTS")
print("=" * 60)

for item in results:

    print(
        f"{item['text']} "
        f"({item['confidence']})"
    )