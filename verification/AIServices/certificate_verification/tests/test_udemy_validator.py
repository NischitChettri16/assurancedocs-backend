from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.verification.udemy_validator import (
    UdemyValidator
)

validator = UdemyValidator()

url = (
    "https://www.udemy.com/certificate/UC-3f3615fc-9509-48de-8b4f-ef9c7ea1f5ff/"
)

result = validator.validate(url)

print()
print("=" * 50)
print("UDEMY PAGE DATA")
print("=" * 50)

print(result)