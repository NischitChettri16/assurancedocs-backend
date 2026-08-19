class AuthenticityScorer:

    def calculate(
        self,
        platform,
        url_valid,
        course_similarity,
        logos,
        stamps,
        signatures,
    ):

        score = 0

        # -----------------------------
        # URL Verification
        # -----------------------------

        if url_valid:
            score += 30

        # -----------------------------
        # Course Match
        # -----------------------------

        score += int(course_similarity * 40)

        # -----------------------------
        # Platform Specific Rules
        # -----------------------------

        if platform == "coursera":

            if len(logos) > 0:
                score += 10

            if len(stamps) > 0:
                score += 10

            if len(signatures) > 0:
                score += 10

        elif platform == "udemy":

            if len(logos) > 0:
                score += 30

            # Udemy certificates usually
            # don't contain stamps/signatures

        else:

            if len(logos) > 0:
                score += 10

            if len(stamps) > 0:
                score += 10

            if len(signatures) > 0:
                score += 10

        score = min(score, 100)

        # -----------------------------
        # Decision
        # -----------------------------

        if score >= 80:
            decision = "GENUINE"

        elif score >= 50:
            decision = "SUSPICIOUS"

        else:
            decision = "FAKE"

        return {
            "score": score,
            "decision": decision,
        }