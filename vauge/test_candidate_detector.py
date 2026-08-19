import cv2

from assurancedocsbackend.vauge.candidate_detector import CandidateDetector
from assurancedocsbackend.vauge.box_merger import BoxMerger

detector = CandidateDetector()
merger = BoxMerger()

image, mask, candidates = detector.detect(
    r"..\datasets\original\genuine\Google\google_0002.jpg"
)

print("Before merge:", len(candidates))

merged = merger.merge(candidates)

print("After merge:", len(merged))

result = detector.visualize(image, merged)

cv2.imshow("Mask", mask)
cv2.imshow("Merged", result)

cv2.waitKey(0)
cv2.destroyAllWindows()