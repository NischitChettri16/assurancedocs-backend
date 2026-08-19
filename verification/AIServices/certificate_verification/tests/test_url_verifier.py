from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)

from verification.AIServices.certificate_verification.verification.url_verifier import URLVerifier


url = "https://www.udemy.com/certificate/UC-3f3615fc-9509-48de-8b4f-ef9c7ea1f5ff/"

verifier = URLVerifier()

result = verifier.verify(url,"udemy")

print()
print("=" * 50)
print("URL VERIFICATION")
print("=" * 50)

for k, v in result.items():
    print(f"{k}: {v}")