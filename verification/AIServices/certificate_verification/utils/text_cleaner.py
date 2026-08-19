import re


class TextCleaner:

    @staticmethod
    def clean(text):

        text = re.sub(r"\s+", " ", text)

        text = text.replace("Creat or", "Creator")

        text = text.replace("Develop er", "Developer")

        text = text.replace("Engin eer", "Engineer")

        return text.strip()