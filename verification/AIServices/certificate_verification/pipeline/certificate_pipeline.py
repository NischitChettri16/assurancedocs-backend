# from pathlib import Path
# import sys

# sys.path.append(
#     str(
#         Path(__file__).resolve().parent.parent
#     )
# )

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "best.pt"


from  ..ocr.ocr_engine import OCREngine

from ..classifier.platform_classifier import PlatformClassifier

from  ..classifier.coursera_classifier import (
    CourseraClassifier
)

    
from ..classifier.udemy_classifier  import (
    UdemyClassifier
)

from ..verification.url_extractor import URLExtractor
from ..verification.url_verifier import URLVerifier

from ..verification.coursera_validator import (
    CourseraValidator
)
from  ..verification.udemy_validator import(
    UdemyValidator
)

from  ..matching.field_matcher import (
    FieldMatcher
)

from ..detection.certificate_detector import (
    CertificateDetector
)

from ..scoring.authenticity_scorer import (
    AuthenticityScorer
)


class CertificatePipeline:

    def __init__(self):

        self.ocr = OCREngine()

        self.platform_classifier = (
            PlatformClassifier()
        )

        self.coursera_classifier = (
            CourseraClassifier()
        )

        self.udemy_classifier = (
            UdemyClassifier()
        )

        self.url_extractor = (
            URLExtractor()
        )

        self.url_verifier = (
            URLVerifier()
        )

        self.coursera_validator = (
            CourseraValidator()
        )
        self.udemy_validator=(
            UdemyValidator()
        )

        self.matcher = (
            FieldMatcher()
        )

        self.detector = (
            CertificateDetector(
                model_path=str(MODEL_PATH)
            )
        )
        

        self.scorer = (
            AuthenticityScorer()
        )

    def verify(
    self,
    image_path,
    progress_callback=None,
):

     def update_progress(value):
        if progress_callback:
            progress_callback(value)

    # OCR
     update_progress(10)

     ocr_results = self.ocr.extract_text(
         image_path
     )

     # Platform Detection
     update_progress(20)

     platform = (
         self.platform_classifier.classify(
             ocr_results
         )
     )

     # Field Extraction
     update_progress(35)

     if platform["platform"] == "coursera":

         fields = (
             self.coursera_classifier.classify(
                 ocr_results
             )
         )

     elif platform["platform"] == "udemy":

        fields = (
            self.udemy_classifier.classify(
                ocr_results
            )
        )

     else:
 
         fields = {}
 
     # URL Extraction
     update_progress(45)
 
     urls = self.url_extractor.extract(
         ocr_results
     )
 
     url = None
 
     if urls:
         url = urls[0]["url"]
 
     url_valid = {
         "valid": False,
         "status_code": None,
         "final_url": None,
     }
 
     similarity = 0
     page_data = None
 
     # URL Verification
     update_progress(55)
 
     if url:
 
         url_valid = (
             self.url_verifier.verify(
                 url,
                 platform=platform["platform"]
             )
         )
 
         if url_valid.get("valid"):
 
             update_progress(65)
 
             if (
                 platform["platform"]
                 == "coursera"
             ):
                 page_data = (
                     self.coursera_validator.validate(
                         url
                     )
                 )
 
             elif (
                 platform["platform"]
                 == "udemy"
             ):
                 page_data = (
                     self.udemy_validator.validate(
                         url
                     )
                 )
 
             update_progress(75)
 
             if (
                 page_data
                 and fields.get(
                     "course_name"
                 )
                 and page_data.get(
                     "course_name"
                 )
             ):
 
                 similarity = (
                     self.matcher.similarity(
                         fields[
                             "course_name"
                         ],
                         page_data[
                             "course_name"
                         ]
                     )
                 )
 
     # Visual Detection
     update_progress(85)
 
     visual = self.detector.detect(
         image_path
     )
 
     # Scoring
     update_progress(95)
 
     score = (
         self.scorer.calculate(
             platform=platform["platform"],
             url_valid=url_valid.get(
                 "valid",
                 False
             ),
             course_similarity=similarity,
             logos=visual["logos"],
             stamps=visual["stamps"],
             signatures=visual[
                 "signatures"
             ],
         )
     )
 
     update_progress(100)
 
     return {
         "platform": platform,
         "fields": fields,
         "url": url,
         "url_valid": url_valid,
         "page_data": page_data,
         "course_similarity": similarity,
         "visual_features": visual,
         "result": score,
     }