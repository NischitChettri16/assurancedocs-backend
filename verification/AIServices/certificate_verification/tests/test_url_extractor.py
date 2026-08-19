from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.ocr.ocr_engine import OCREngine
from verification.AIServices.certificate_verification.verification.url_extractor import URLExtractor


IMAGE_PATH = "../../datasets/test_images/coursera_0001.jpg"

ocr = OCREngine()

ocr_results = ocr.extract_text(
    IMAGE_PATH
)

extractor = URLExtractor()

url = extractor.get_primary_url(
    ocr_results
)

print()
print("=" * 50)
print("URL")
print("=" * 50)
print(url)