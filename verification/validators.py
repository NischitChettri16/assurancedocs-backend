# verification/validators.py

from django.core.exceptions import ValidationError


def validate_file_size(file):

    max_size = 3 * 1024 * 1024  # 3 MB

    if file.size > max_size:
        raise ValidationError(
            "Image size cannot exceed 3 MB."
        )