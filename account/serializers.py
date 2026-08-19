from rest_framework import serializers

from account.models import User

from django.contrib.auth import authenticate

from rest_framework import serializers

from account.models import (
    UserRole
)


class CreateHRSerializer(
    serializers.Serializer
):

    first_name = serializers.CharField()

    last_name = serializers.CharField()

    email = serializers.EmailField()

    phone = serializers.CharField(
        required=False,
        allow_blank=True
    )

    def validate_email(
        self,
        value
    ):

        if User.objects.filter(
            email=value
        ).exists():

            raise serializers.ValidationError(
                "Email already exists."
            )

        return value






class HRLoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    def validate(
        self,
        attrs
    ):

        email = attrs.get(
            "email"
        )

        password = attrs.get(
            "password"
        )

        user = authenticate(
            email=email,
            password=password
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid credentials."
            )

        if not user.is_active:

            raise serializers.ValidationError(
                "Account is disabled."
            )

        if (
            user.role
            != UserRole.HR
        ):

            raise serializers.ValidationError(
                "HR account required."
            )

        attrs["user"] = user

        return attrs