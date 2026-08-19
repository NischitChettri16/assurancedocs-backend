from pathlib import Path
import sys

sys.path.append(
    str(
        Path(__file__).resolve().parent.parent
    )
)


from verification.AIServices.certificate_verification.annotation.manual_annotation_tool import AnnotationTool

tool = AnnotationTool(
    r"..\datasets\images\train"
)

tool.open()