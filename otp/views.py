from datetime import timedelta

from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OTP
from .serializers import (
    SendOTPSerializer
)
from core.services.email_services import(
    EmailService
)
from rest_framework.permissions import AllowAny,IsAuthenticated
from utils.generateOTP import generate_otp



from .serializers import (
    VerifyOTPSerializer
)


class SendOTPView(APIView):
    authentication_classes=[]
    permission_classes=[AllowAny]
    def post(
        self,
        request
    ):

        serializer = (
            SendOTPSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = (
            serializer.validated_data[
                "email"
            ]
        )

        otp = generate_otp()

        OTP.objects.create(
            email=email,
            otp=otp,
            expires_at=
                timezone.now()
                + timedelta(
                    minutes=10
                )
        )

        # TODO:
        # send email here
        EmailService.send_otp_email(
            email=email,
            otp=otp
        )

        print(
            f"OTP for {email}: {otp}"
        )

        return Response(
            {
                "success":True,
                "message":
                "OTP sent successfully."
            }
        )





class VerifyOTPView(
    APIView
):
    permission_classes=[AllowAny]

    def post(
        self,
        request
    ):

        serializer = (
            VerifyOTPSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        email = (
            serializer.validated_data[
                "email"
            ]
        )

        otp = (
            serializer.validated_data[
                "otp"
            ]
        )

        otp_obj = OTP.objects.filter(
            email=email,
            otp=otp,
            is_verified=False
        ).order_by(
            "-created_at"
        ).first()

        if not otp_obj:

            return Response(
                {
                    "success":False,
                    "message":
                    "Invalid OTP"
                },
                status=400
            )

        if (
            otp_obj.expires_at
            < timezone.now()
        ):

            return Response(
                {
                    "success":False,
                    "message":
                    "OTP expired"
                },
                status=400
            )

        otp_obj.is_verified = True
        otp_obj.save()

        return Response(
            {
                "success":True,
                "message":
                "OTP verified successfully"
            }
        )