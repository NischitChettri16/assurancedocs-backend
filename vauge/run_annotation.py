from manual_annotation_tool import AnnotationTool

if __name__ == "__main__":

    tool = AnnotationTool(
        image_directory="../datasets/images/train"
    )

    tool.open()