from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.scoring.authenticity_scorer import (
    AuthenticityScorer
)

scorer = AuthenticityScorer()

result = scorer.calculate(
    url_valid=True,
    course_similarity=1.0,
    logos=[1],
    stamps=[1],
    signatures=[1],
)

print()
print("=" * 50)
print("AUTHENTICITY RESULT")
print("=" * 50)
print(result)