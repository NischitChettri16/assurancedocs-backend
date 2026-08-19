from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim


class FieldMatcher:

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    # ---------------------------------

    def similarity(
        self,
        text1,
        text2,
    ):

        if not text1 or not text2:
            return 0.0

        emb1 = self.model.encode(
            text1,
            convert_to_tensor=True,
        )

        emb2 = self.model.encode(
            text2,
            convert_to_tensor=True,
        )

        score = cos_sim(
            emb1,
            emb2,
        ).item()

        return round(score, 4)

    # ---------------------------------

    def is_match(
        self,
        text1,
        text2,
        threshold=0.80,
    ):

        score = self.similarity(
            text1,
            text2,
        )

        return {
            "match": score >= threshold,
            "similarity": score,
        }