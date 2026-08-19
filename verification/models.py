# verification/models.py

import uuid

from django.db import models

from account.models import User
from company.models import Company
from .validators import (
    validate_file_size
)

class Verification(models.Model):
    
    STATUS_CHOICES = (
        ("PENDING", "PENDING"),
        ("PROCESSING", "PROCESSING"),
        ("COMPLETED", "COMPLETED"),
        ("FAILED", "FAILED"),
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    progress = models.PositiveIntegerField(
        default=0
    )
    error_message = models.TextField(
        blank=True,
        null=True,
    )

      
    DECISIONS = (
        ("GENUINE", "GENUINE"),
        ("SUSPICIOUS", "SUSPICIOUS"),
        ("FAKE", "FAKE"),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="verifications",
    )

    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="verifications",
    )

    certificate = models.FileField(
        upload_to="certificates/",
        validators=[validate_file_size]
    )

    platform = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    student_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    course_name = models.CharField(
        max_length=500,
        blank=True,
        null=True,
    )

    issuer = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    verification_url = models.TextField(
        blank=True,
        null=True,
    )

    url_valid = models.BooleanField(
        default=False
    )

    authenticity_score = models.IntegerField(
        default=0
    )

    decision = models.CharField(
        max_length=20,
        choices=DECISIONS,
    )

    raw_result = models.JSONField(
        default=dict
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.student_name} - "
            f"{self.decision}"
        )