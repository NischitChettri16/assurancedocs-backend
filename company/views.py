from django.shortcuts import render


from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.password_validation import (
    validate_password
)

from django.core.exceptions import (
    ValidationError
)


from .serializers import CompanySignupSerializer
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LoginSerializer
from django.utils import timezone
from rest_framework.permissions import AllowAny
from utils.auth_response import create_auth_response
from django.core.paginator import Paginator
from django.db.models import Q
import os
import uuid
from django.core.files.base import ContentFile



class CompanySignupView(APIView):
    authentication_classes=[]
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = CompanySignupSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.save()
        return create_auth_response(
            user=user,
            message="Signup Successful."
        )

       

class CompanyLoginView(APIView):

    permission_classes = [AllowAny]

    def post(
        self,
        request
    ):

        serializer = LoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]
        return create_auth_response(
            user=user,
            message="Login Successful."
        )



# company/views.py

from django.db.models import Count
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from account.models import User
from verification.models import Verification



class CompanyDashboardView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        company = request.user.company

        # -----------------------
        # HR Count
        # -----------------------

        total_hrs = (
            User.objects.filter(
                company=company,
                role="HR"
            ).count()
        )

        # -----------------------
        # Current Month
        # -----------------------

        now = timezone.now()

        monthly_verifications = (
            Verification.objects.filter(
                company=company,
                created_at__year=now.year,
                created_at__month=now.month,
            ).count()
        )

        # -----------------------
        # Recent Verifications
        # -----------------------

        recent_verifications = (
            Verification.objects
            .filter(
                company=company
            )
            .order_by(
                "-created_at"
            )[:10]
        )

        recent_data = []

        for verification in recent_verifications:

            recent_data.append(
                {
                    "id": str(
                        verification.id
                    ),

                    "student_name":
                        verification.student_name,

                    "course_name":
                        verification.course_name,

                    "decision":
                        verification.decision,

                    "score":
                        verification.authenticity_score,

                    "created_at":
                        verification.created_at,
                }
            )

        return Response(
            {
                "success": True,

                "stats": {
                    "total_hrs":
                        total_hrs,

                    "verified_this_month":
                        monthly_verifications,
                },

                "recent_verifications":
                    recent_data,
            },

            status=status.HTTP_200_OK
        )



class CompanyHRListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        company = request.user.company

        search = request.GET.get(
            "search",
            ""
        )

        page = int(
            request.GET.get(
                "page",
                1
            )
        )

        page_size = int(
            request.GET.get(
                "page_size",
                10
            )
        )

        queryset = (
            User.objects.filter(
                company=company
            ).exclude(
                role="COMPANY_ADMIN"
            )
        )

        # ---------------------
        # Search
        # ---------------------

        if search:

            queryset = (
                queryset.filter(
                    Q(first_name__icontains=search)
                    |
                    Q(last_name__icontains=search)
                    |
                    Q(email__icontains=search)
                )
            )

        queryset = queryset.order_by(
            "-created_at"
        )

        # ---------------------
        # Pagination
        # ---------------------

        paginator = Paginator(
            queryset,
            page_size
        )

        current_page = (
            paginator.get_page(
                page
            )
        )

        results = []

        for hr in current_page:

            results.append(
                {
                    "id": str(
                        hr.id
                    ),
                    "first_name": (
                        hr.first_name
                    ),
                    "last_name": (
                        hr.last_name
                    ),
                    "email": (
                        hr.email
                    ),
                    "is_active":(
                        hr.is_active
                    ),
                    "phone":{
                        hr.phone
                    }
                }
            )

        return Response(
            {
                "success": True,
                "results": results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (
                        paginator.num_pages
                    ),
                    "total_records": (
                        paginator.count
                    ),
                    "has_next": (
                        current_page.has_next()
                    ),
                    "has_previous": (
                        current_page.has_previous()
                    ),
                },
            }
        )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from company.models import Company
from account.models import User
from verification.models import Verification


class CompanyProfileView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        company = request.user.company

        # -----------------------
        # HR Count
        # -----------------------

        total_hrs = (
            User.objects.filter(
                company=company,
                role="HR"
            ).count()
        )

        # -----------------------
        # Total Verifications
        # -----------------------

        total_verifications = (
            Verification.objects.filter(
                company=company
            ).count()
        )

        # -----------------------
        # Current Month
        # -----------------------

        now = timezone.now()

        verified_this_month = (
            Verification.objects.filter(
                company=company,
                created_at__year=now.year,
                created_at__month=now.month,
            ).count()
        )

        return Response(
            {
                "success": True,

                "company": {
                    "id":
                        str(company.id),

                    "name":
                        company.name,

                    "email":
                        company.email,

                    "phone":
                        company.phone,

                    "website":
                        company.website,

                    "logo": (
                        company.logo.url
                        if company.logo
                        else None
                    ),

                    "is_active":
                        company.is_active,

                    "created_at":
                        company.created_at,

                    # Stats
                    "total_hrs":
                        total_hrs,

                    "total_verifications":
                        total_verifications,

                    "verified_this_month":
                        verified_this_month,
                },
            },
            status=status.HTTP_200_OK
        )



class UpdateCompanyProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request):

        company = request.user.company
        print(company)

        company.name = request.data.get(
            "name",
            company.name
        )

        company.phone = request.data.get(
            "phone",
            company.phone
        )

        company.website = request.data.get(
            "website",
            company.website
        )

        logo = request.FILES.get(
            "logo"
        )
        print(logo)


        if logo:

            # delete old logo
            if company.logo:
                company.logo.delete(
                    save=False
                )

            extension = os.path.splitext(
                logo.name
            )[1]

            filename = (
                f"company_{company.id}"
                f"{extension}"
            )

            company.logo.save(
                filename,
                ContentFile(
                    logo.read()
                ),
                save=False
            )

        company.save()

        return Response(
            {
                "success": True,
                "message": "Company profile updated successfully.",
                "company": {
                    "id": str(company.id),
                    "name": company.name,
                    "email": company.email,
                    "phone": company.phone,
                    "website": company.website,
                    "logo": (
                        company.logo.url
                        if company.logo
                        else None
                    ),
                },
            },
            status=status.HTTP_200_OK,
        )
        
        



class ChangePasswordView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        user = request.user

        old_password = request.data.get(
            "old_password"
        )

        new_password = request.data.get(
            "new_password"
        )

        confirm_password = request.data.get(
            "confirm_password"
        )

        if (
            not old_password
            or not new_password
            or not confirm_password
        ):
            return Response(
                {
                    "success": False,
                    "message":
                        "All fields are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(
            old_password
        ):
            return Response(
                {
                    "success": False,
                    "message":
                        "Current password is incorrect."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            new_password
            != confirm_password
        ):
            return Response(
                {
                    "success": False,
                    "message":
                        "New password and confirm password do not match."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            validate_password(
                new_password,
                user
            )

        except ValidationError as e:

            return Response(
                {
                    "success": False,
                    "message":
                        list(e.messages)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(
            new_password
        )

        user.save()

        return Response(
            {
                "success": True,
                "message":
                    "Password changed successfully."
            },
            status=status.HTTP_200_OK
        )

