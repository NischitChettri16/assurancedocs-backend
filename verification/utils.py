class VerificationMessageGenerator:

    @staticmethod
    def generate(
        platform,
        url_valid,
        course_similarity,
        logos,
        stamps,
        signatures,
        fields,
        score,
        decision,
    ):

        issues = []
        strengths = []

        # Platform
        if platform != "unknown":
            strengths.append(
                f"Platform identified as {platform.title()}."
            )
        else:
            issues.append(
                "Certificate platform could not be identified."
            )

        # URL Validation
        if url_valid:
            strengths.append(
                "Verification URL was successfully validated."
            )
        else:
            issues.append(
                "Verification URL could not be validated."
            )

        # Course Similarity
        if course_similarity >= 0.90:
            strengths.append(
                "Course information matches the official verification page."
            )
        elif course_similarity >= 0.70:
            issues.append(
                "Course information partially matches the verification page."
            )
        else:
            issues.append(
                "Course information does not match the verification page."
            )

        # Logo
        if logos:
            strengths.append(
                "Certificate logo was detected."
            )
        else:
            issues.append(
                "No logo was detected. The logo may be missing or image quality may be poor."
            )

        # Signature
        if signatures:
            strengths.append(
                "Signature was detected."
            )
        else:
            issues.append(
                "No signature was detected. The signature may be unclear or missing."
            )

        # Stamp
        if stamps:
            strengths.append(
                "Stamp or seal was detected."
            )
        else:
            issues.append(
                "No stamp was detected. The stamp may be missing or difficult to identify."
            )

        # OCR Fields
        if not fields.get("student_name"):
            issues.append(
                "Student name could not be extracted."
            )

        if not fields.get("course_name"):
            issues.append(
                "Course name could not be extracted."
            )

        if not fields.get("issuer"):
            issues.append(
                "Issuer information could not be extracted."
            )

        # Final Message
        if decision == "GENUINE":
            summary = (
                "The certificate appears authentic because most verification checks passed successfully."
            )

        elif decision == "SUSPICIOUS":
            summary = (
                "The certificate contains some inconsistencies and should be reviewed manually."
            )

        else:
            summary = (
                "The certificate failed multiple verification checks and may be fraudulent."
            )

        return {
            "score": score,
            "decision": decision,
            "summary": summary,
            "strengths": strengths,
            "issues": issues,
        }