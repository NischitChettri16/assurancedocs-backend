from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.verification.coursera_validator import CourseraValidator


url = "https://www.coursera.org/account/accomplishments/verify/1W07B1WE21PY"

validator = CourseraValidator()

result = validator.validate(url)

print()
print("=" * 50)
print("COURSERA DATA")
print("=" * 50)

print(result)