import traceback

from .models import Verification

from verification.AIServices.certificate_verification.pipeline.certificate_pipeline import (
    CertificatePipeline,
)


def update_progress(
    verification,
    progress,
    status="PROCESSING",
):
    verification.progress = progress
    verification.status = status

    verification.save(
        update_fields=[
            "progress",
            "status",
        ]
    )


def process_verification(
    verification_id,
):

    verification = (
        Verification.objects.get(
            id=verification_id
        )
    )

    try:

        # ----------------------------------
        # Mark Processing Started
        # ----------------------------------

        update_progress(
            verification,
            1,
            "PROCESSING",
        )

        pipeline = (
            CertificatePipeline()
        )

        # ----------------------------------
        # Run Pipeline
        # ----------------------------------

        result = pipeline.verify(
            verification.certificate.path,
            progress_callback=lambda p:
                update_progress(
                    verification,
                    p,
                )
        )

        fields = result.get(
            "fields",
            {}
        )

        # ----------------------------------
        # Save Result
        # ----------------------------------

        verification.platform = (
            result.get(
                "platform",
                {}
            ).get(
                "platform"
            )
        )

        verification.student_name = (
            fields.get(
                "student_name"
            )
        )

        verification.course_name = (
            fields.get(
                "course_name"
            )
        )

        verification.issuer = (
            fields.get(
                "issuer"
            )
        )

        verification.verification_url = (
            fields.get(
                "verification_url"
            )
        )

        # url_valid is now always a dict
        verification.url_valid = (
            result.get(
                "url_valid",
                {}
            ).get(
                "valid",
                False
            )
        )

        verification.authenticity_score = (
            result.get(
                "result",
                {}
            ).get(
                "score",
                0
            )
        )

        verification.decision = (
            result.get(
                "result",
                {}
            ).get(
                "decision",
                "FAKE"
            )
        )

        verification.raw_result = result

        verification.progress = 100
        verification.status = (
            "COMPLETED"
        )

        verification.save()

        print(
            f"Verification completed: "
            f"{verification.id}"
        )

    except Exception as e:

        verification.status = (
            "FAILED"
        )

        verification.raw_result = {
            "error": str(e),
            "traceback": traceback.format_exc(),
        }

        verification.save(
            update_fields=[
                "status",
                "raw_result",
            ]
        )

        print(
            f"Verification failed: "
            f"{verification.id}"
        )

        print(
            traceback.format_exc()
        )