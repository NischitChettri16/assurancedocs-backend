from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework import serializers
from account.models import (
    User,
    UserRole
)
from django.utils import timezone


from company.models import Company

from otp.models import OTP



class CompanySignupSerializer(
    serializers.Serializer
):

    company_name = serializers.CharField()

    company_email = serializers.EmailField()

    first_name = serializers.CharField()

    last_name = serializers.CharField()

    email = serializers.EmailField()

    password = serializers.CharField(
        write_only=True
    )

    otp = serializers.CharField(
        max_length=6
    )
    def validate(self, attrs):

      email = attrs["email"]
      otp = attrs["otp"]
  
      if User.objects.filter(
          email=email
      ).exists():
  
          raise serializers.ValidationError(
              {
                  "email":
                  "Email already exists."
              }
          )
  
      otp_obj = OTP.objects.filter(
          email=email,
          otp=otp
      ).order_by(
          "-created_at"
      ).first()
  
      if not otp_obj:
  
          raise serializers.ValidationError(
              {
                  "otp":
                  "Invalid OTP."
              }
          )
  
      if (
          otp_obj.expires_at
          < timezone.now()
      ):
  
          raise serializers.ValidationError(
              {
                  "otp":
                  "OTP has expired."
              }
          )
  
      return attrs



    def create(
    self,
    validated_data
      ):

      otp = validated_data.pop(
          "otp"
      )
  
      company = Company.objects.create(
          name=validated_data[
              "company_name"
          ],
          email=validated_data[
              "company_email"
          ]
      )
  
      user = User.objects.create_user(
          email=validated_data[
              "email"
          ],
          password=validated_data[
              "password"
          ],
          first_name=validated_data[
              "first_name"
          ],
          last_name=validated_data[
              "last_name"
          ],
          role=UserRole.COMPANY_ADMIN,
          company=company
      )
  
      OTP.objects.filter(
          email=user.email,
          otp=otp
      ).delete()
  
      return user




class LoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField()

    password = serializers.CharField()

    def validate(
        self,
        attrs
    ):

        user = authenticate(
            email=attrs["email"],
            password=attrs["password"]
        )

        if not user:

            raise serializers.ValidationError(
                "Invalid credentials."
            )

        attrs["user"] = user

        return attrs