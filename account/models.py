import uuid

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    use_in_migrations = True

    def create_user(
        self,
        email,
        password=None,
        **extra_fields
    ):

        if not email:
            raise ValueError(
                "Email is required"
            )

        email = self.normalize_email(
            email
        )

        user = self.model(
            email=email,
            **extra_fields
        )

        user.set_password(password)

        user.save(
            using=self._db
        )

        return user

    def create_superuser(
        self,
        email,
        password=None,
        **extra_fields
    ):

        extra_fields.setdefault(
            "is_staff",
            True
        )

        extra_fields.setdefault(
            "is_superuser",
            True
        )

        extra_fields.setdefault(
            "is_active",
            True
        )

        extra_fields.setdefault(
            "role",
            UserRole.SUPER_ADMIN
        )

        return self.create_user(
            email,
            password,
            **extra_fields
        )


class UserRole(models.TextChoices):

    SUPER_ADMIN = (
        "SUPER_ADMIN",
        "Super Admin"
    )

    COMPANY_ADMIN = (
        "COMPANY_ADMIN",
        "Company Admin"
    )

    HR = (
        "HR",
        "HR"
    )


class User(
    AbstractBaseUser,
    PermissionsMixin
):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    company = models.ForeignKey(
        "company.Company",
        on_delete=models.CASCADE,
        related_name="users",
        null=True,
        blank=True
    )

    email = models.EmailField(
        unique=True
    )

    first_name = models.CharField(
        max_length=100
    )

    last_name = models.CharField(
        max_length=100
    )

    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.HR
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    is_active = models.BooleanField(
        default=True
    )

    is_staff = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    objects = UserManager()

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return (
            f"{self.first_name} "
            f"{self.last_name}"
        )

import hashlib
import uuid

from django.conf import settings
from django.db import models


class HRPasswordSetupToken(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_setup_tokens",
    )

    email = models.EmailField()

    token_hash = models.CharField(
        max_length=64,
        unique=True,
    )

    expires_at = models.DateTimeField()

    used = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.email

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(
            token.encode()
        ).hexdigest()

