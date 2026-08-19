from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.matching.field_matcher import FieldMatcher


matcher = FieldMatcher()

ocr_course = "Canva for college students"

verified_course = "Canva for college students"

result = matcher.is_match(
    ocr_course,
    verified_course,
)

print()
print("=" * 50)
print("FIELD MATCH")
print("=" * 50)
print(result)