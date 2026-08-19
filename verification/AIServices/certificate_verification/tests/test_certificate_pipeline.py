import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__).resolve()
        .parent.parent
    )
)


from verification.AIServices.certificate_verification.pipeline.certificate_pipeline import (
    CertificatePipeline
)

IMAGE_PATH = (
    "../../datasets/fake_images/fake_0001.jpg"
)

pipeline = CertificatePipeline()

result = pipeline.verify(
    IMAGE_PATH
)

print()
print("=" * 60)
print("VERIFICATION RESULT")
print("=" * 60)

print()

print("Platform:")
print(result["platform"])

print()

print("URL:")
print(result["url"])

print()

print("URL Valid:")
print(result["url_valid"])

print()

print("Course Similarity:")
print(result["course_similarity"])

print()

print("Fields:")
print(result["fields"])

print()

print("Visual Features:")
print(result["visual_features"])

print()

print("Final Result:")
print(result["result"])