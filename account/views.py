import secrets
import string

from django.db.models import Q
from django.core.paginator import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework_simplejwt.tokens import (
    RefreshToken
)
from rest_framework import status
from django.utils import timezone
from django.conf import settings


from account.models import (
    User,
    UserRole,
    HRPasswordSetupToken
)
from verification.models import Verification

from .serializers import (
    CreateHRSerializer,
    HRLoginSerializer
)

from django.contrib.auth.password_validation import (
    validate_password
)
from django.core.exceptions import (
    ValidationError
)


# from core.permissions import (
#     IsCompanyAdmin
# )

from core.services.email_services import (
    EmailService
)


class CreateHRView(
    APIView
):

    permission_classes = [
        IsAuthenticated]

    def generate_password(self):

        alphabet = (
            string.ascii_letters
            + string.digits
        )

        return "".join(
            secrets.choice(
                alphabet
            )
            for _ in range(10)
        )

    def post(
        self,
        request
    ):

        serializer = (
            CreateHRSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        temp_password = (
            self.generate_password()
        )

        user = User.objects.create_user(
            email=serializer.validated_data[
                "email"
            ],

            password=temp_password,

            first_name=serializer.validated_data[
                "first_name"
            ],

            last_name=serializer.validated_data[
                "last_name"
            ],

            phone=serializer.validated_data.get(
                "phone",
                ""
            ),

            role=UserRole.HR,

            company=request.user.company
        )

        EmailService.send_hr_invitation(
            email=user.email,
            password=temp_password,
            company=request.user.company.name
        )

        return Response(
            {
                "success":True,
                "message":
                "HR created successfully."
            }
        )
        
        
        


class HRLoginView(APIView):

    permission_classes = []
    authentication_classes = []

    def post(
        self,
        request
    ):

        serializer = HRLoginSerializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        user = serializer.validated_data[
            "user"
        ]

        # ----------------------------------
        # Ensure HR account
        # ----------------------------------

        if (
            user.role
            != UserRole.HR
        ):

            return Response(
                {
                    "success": False,
                    "message":
                        "HR account required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ----------------------------------
        # Generate JWT tokens
        # ----------------------------------

        refresh = RefreshToken.for_user(
            user
        )

        access = (
            refresh.access_token
        )

        # ----------------------------------
        # Response
        # ----------------------------------

        response = Response(
            {
                "success": True,

                "message":
                    "Login Successful.",

                "user": {
                    "id":
                        str(user.id),

                    "email":
                        user.email,

                    "first_name":
                        user.first_name,

                    "last_name":
                        user.last_name,

                    "role":
                        user.role,

                    "company": (
                        {
                            "id":
                                str(
                                    user.company.id
                                ),

                            "name":
                                user.company.name,
                        }
                        if user.company
                        else None
                    ),
                },
            },
            status=status.HTTP_200_OK
        )

        # ----------------------------------
        # Access cookie
        # ----------------------------------

        response.set_cookie(
            key="access",

            value=str(access),

            max_age=2 * 24 * 60 * 60,

            path=settings.AUTH_COOKIE_PATH,

            secure=settings.AUTH_COOKIE_SECURE,

            httponly=settings.AUTH_COOKIE_HTTP_ONLY,

            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        # ----------------------------------
        # Refresh cookie
        # ----------------------------------

        response.set_cookie(
            key="refresh",

            value=str(refresh),

            max_age=7 * 24 * 60 * 60,

            path=settings.AUTH_COOKIE_PATH,

            secure=settings.AUTH_COOKIE_SECURE,

            httponly=settings.AUTH_COOKIE_HTTP_ONLY,

            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        return response


class LogoutView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        response = Response(
            {
                "success": True,
                "message": "Logged out successfully."
            }
        )

        # access token cookie
        response.delete_cookie(
            settings.AUTH_COOKIE,
            path=settings.AUTH_COOKIE_PATH,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        # refresh token cookie
        response.delete_cookie(
            "refresh",
            path=settings.AUTH_COOKIE_PATH,
            samesite=settings.AUTH_COOKIE_SAMESITE,
        )

        # csrf cookie (if used)
        response.delete_cookie(
            "csrftoken"
        )

        return response
    




class HRDashboardStatsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        hr = request.user

        # -----------------------------------------
        # Current date
        # -----------------------------------------

        now = timezone.now()

        current_year = now.year
        current_month = now.month

        # -----------------------------------------
        # Current month boundaries
        # -----------------------------------------

        current_month_start = now.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        # -----------------------------------------
        # Previous month
        # -----------------------------------------

        if current_month == 1:

            previous_month_year = (
                current_year - 1
            )

            previous_month = 12

        else:

            previous_month_year = (
                current_year
            )

            previous_month = (
                current_month - 1
            )

        previous_month_start = (
            current_month_start.replace(
                year=previous_month_year,
                month=previous_month
            )
        )

        # -----------------------------------------
        # Base queryset
        #
        # IMPORTANT:
        # Only verifications performed by
        # the logged-in HR.
        # -----------------------------------------

        queryset = Verification.objects.filter(
            verified_by=hr
        )

        # -----------------------------------------
        # Current month
        # -----------------------------------------

        current_month_queryset = queryset.filter(
            created_at__gte=current_month_start
        )

        # -----------------------------------------
        # Previous month
        # -----------------------------------------

        previous_month_queryset = queryset.filter(
            created_at__gte=previous_month_start,
            created_at__lt=current_month_start
        )

        # -----------------------------------------
        # Current statistics
        # -----------------------------------------

        total_verifications = (
            current_month_queryset.count()
        )

        genuine = (
            current_month_queryset.filter(
                decision="GENUINE"
            ).count()
        )

        suspicious = (
            current_month_queryset.filter(
                decision="SUSPICIOUS"
            ).count()
        )

        fraudulent = (
            current_month_queryset.filter(
                decision="FAKE"
            ).count()
        )

        # -----------------------------------------
        # Previous statistics
        # -----------------------------------------

        previous_total = (
            previous_month_queryset.count()
        )

        previous_genuine = (
            previous_month_queryset.filter(
                decision="GENUINE"
            ).count()
        )

        previous_suspicious = (
            previous_month_queryset.filter(
                decision="SUSPICIOUS"
            ).count()
        )

        previous_fraudulent = (
            previous_month_queryset.filter(
                decision="FAKE"
            ).count()
        )

        # -----------------------------------------
        # Percentage helper
        # -----------------------------------------

        def calculate_change(
            current,
            previous
        ):

            if previous == 0:

                if current == 0:
                    return 0

                return 100

            change = (
                (
                    current - previous
                )
                / previous
            ) * 100

            return round(
                change,
                1
            )

        # -----------------------------------------
        # Monthly changes
        # -----------------------------------------

        total_change = calculate_change(
            total_verifications,
            previous_total
        )

        genuine_change = calculate_change(
            genuine,
            previous_genuine
        )

        suspicious_change = calculate_change(
            suspicious,
            previous_suspicious
        )

        fraudulent_change = calculate_change(
            fraudulent,
            previous_fraudulent
        )

        # -----------------------------------------
        # Response
        # -----------------------------------------

        return Response(
            {
                "success": True,

                "stats": {

                    "total_verifications": {
                        "count":
                            total_verifications,

                        "change":
                            total_change,

                        "change_type":
                            (
                                "increase"
                                if total_change > 0
                                else
                                "decrease"
                                if total_change < 0
                                else
                                "neutral"
                            ),
                    },

                    "genuine": {
                        "count":
                            genuine,

                        "change":
                            genuine_change,

                        "change_type":
                            (
                                "increase"
                                if genuine_change > 0
                                else
                                "decrease"
                                if genuine_change < 0
                                else
                                "neutral"
                            ),
                    },

                    "suspicious": {
                        "count":
                            suspicious,

                        "change":
                            suspicious_change,

                        "change_type":
                            (
                                "increase"
                                if suspicious_change > 0
                                else
                                "decrease"
                                if suspicious_change < 0
                                else
                                "neutral"
                            ),
                    },

                    "fraudulent": {
                        "count":
                            fraudulent,

                        "change":
                            fraudulent_change,

                        "change_type":
                            (
                                "increase"
                                if fraudulent_change > 0
                                else
                                "decrease"
                                if fraudulent_change < 0
                                else
                                "neutral"
                            ),
                    },
                }
            },
            status=status.HTTP_200_OK
        )
        



class HRVerificationListView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        hr = request.user

        search = request.GET.get(
            "search",
            ""
        ).strip()

        decision = request.GET.get(
            "decision",
            ""
        ).strip()

        platform = request.GET.get(
            "provider",
            ""
        ).strip()

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

        # ----------------------------------
        # Only verifications done by
        # the logged-in HR
        # ----------------------------------

        queryset = (
            Verification.objects
            .filter(
                verified_by=hr
            )
            .select_related(
                "verified_by"
            )
            .order_by(
                "-created_at"
            )
        )

        # ----------------------------------
        # Search
        # ----------------------------------

        if search:

            queryset = queryset.filter(
                Q(student_name__icontains=search)
                |
                Q(course_name__icontains=search)
                |
                Q(platform__icontains=search)
                |
                Q(decision__icontains=search)
            )

        # ----------------------------------
        # Decision Filter
        # ----------------------------------

        if decision:

            queryset = queryset.filter(
                decision__iexact=decision
            )

        # ----------------------------------
        # Platform Filter
        # ----------------------------------

        if platform:

            queryset = queryset.filter(
                platform__iexact=platform
            )

        # ----------------------------------
        # Pagination
        # ----------------------------------

        paginator = Paginator(
            queryset,
            page_size
        )

        current_page = (
            paginator.get_page(
                page
            )
        )

        # ----------------------------------
        # Results
        # ----------------------------------

        results = []

        for verification in current_page:

            results.append(
                {
                    "id": str(
                        verification.id
                    ),

                    "student_name":
                        verification.student_name,

                    "course_name":
                        verification.course_name,

                    "platform":
                        verification.platform,

                    "authenticity_score":
                        verification.authenticity_score,

                    "decision":
                        verification.decision,

                    "verification_url":
                        verification.verification_url,

                    "url_valid":
                        verification.url_valid,

                    "certificate": (
                        verification.certificate.url
                        if verification.certificate
                        else None
                    ),

                    "created_at":
                        verification.created_at,

                    "verified_by_id": (
                        str(
                            verification.verified_by_id
                        )
                        if verification.verified_by_id
                        else None
                    ),
                }
            )

        # ----------------------------------
        # Response
        # ----------------------------------

        return Response(
            {
                "success": True,

                "results": results,

                "pagination": {
                    "page":
                        current_page.number,

                    "page_size":
                        page_size,

                    "total_pages":
                        paginator.num_pages,

                    "total_records":
                        paginator.count,

                    "has_next":
                        current_page.has_next(),

                    "has_previous":
                        current_page.has_previous(),
                },
            },
            status=status.HTTP_200_OK
        )
        


class RecentHRVerificationView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        hr = request.user

        # ----------------------------------
        # Get only this HR's verifications
        # and return the latest 4
        # ----------------------------------

        verifications = (
            Verification.objects
            .filter(
                verified_by=hr
            )
            .order_by(
                "-created_at"
            )[:4]
        )

        results = []

        for verification in verifications:

            results.append(
                {
                    "id": str(
                        verification.id
                    ),

                    "student_name":
                        verification.student_name,

                    "course_name":
                        verification.course_name,

                    "platform":
                        verification.platform,

                    "authenticity_score":
                        verification.authenticity_score,

                    "decision":
                        verification.decision,

                    "verification_url":
                        verification.verification_url,

                    "url_valid":
                        verification.url_valid,

                    "certificate":
                        (
                            verification.certificate.url
                            if verification.certificate
                            else None
                        ),

                    "created_at":
                        verification.created_at,

                }
            )

        return Response(
            {
                "success": True,
                "results": results,
            },
            status=status.HTTP_200_OK
        )
        


class HRVerificationStatsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        hr = request.user

        # Only verifications performed by
        # the currently logged-in HR
        queryset = Verification.objects.filter(
            verified_by=hr
        )

        total_checks = queryset.count()

        genuine = queryset.filter(
            decision="GENUINE"
        ).count()

        suspicious = queryset.filter(
            decision="SUSPICIOUS"
        ).count()

        fraudulent = queryset.filter(
            decision="FAKE"
        ).count()

        return Response(
            {
                "success": True,

                "stats": {
                    "total_checks": total_checks,
                    "genuine": genuine,
                    "suspicious": suspicious,
                    "fraudulent": fraudulent,
                },
            },
            status=status.HTTP_200_OK
        )
        


class UpdateHRPasswordView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        user = request.user

        # ---------------------------------
        # Only HR can use this endpoint
        # ---------------------------------

        if user.role != "HR":

            return Response(
                {
                    "success": False,
                    "message":
                        "Only HR users can update their password."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        old_password = request.data.get(
            "old_password"
        )

        new_password = request.data.get(
            "new_password"
        )

        confirm_password = request.data.get(
            "confirm_password"
        )

        # ---------------------------------
        # Required fields
        # ---------------------------------

        if not all([
            old_password,
            new_password,
            confirm_password,
        ]):

            return Response(
                {
                    "success": False,
                    "message":
                        "All password fields are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------
        # Check current password
        # ---------------------------------

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

        # ---------------------------------
        # Confirm new password
        # ---------------------------------

        if (
            new_password
            != confirm_password
        ):

            return Response(
                {
                    "success": False,
                    "message":
                        "New passwords do not match."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------
        # Validate new password
        # ---------------------------------

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
                        e.messages
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------------------------------
        # Update password
        # ---------------------------------

        user.set_password(
            new_password
        )

        user.save(
            update_fields=[
                "password"
            ]
        )

        return Response(
            {
                "success": True,
                "message":
                    "Password updated successfully."
            },
            status=status.HTTP_200_OK
        )        



class HRProfileView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        hr = request.user

        # ----------------------------------
        # Ensure requested user is HR
        # ----------------------------------

        if hr.role != "HR":

            return Response(
                {
                    "success": False,
                    "message":
                        "Only HR users can access this profile."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        company = getattr(
            hr,
            "company",
            None
        )

        # ----------------------------------
        # HR verification queryset
        # Only this HR's verifications
        # ----------------------------------

        verifications = (
            Verification.objects
            .filter(
                verified_by=hr
            )
        )

        # ----------------------------------
        # Statistics
        # ----------------------------------

        total_verifications = (
            verifications.count()
        )

        genuine = (
            verifications
            .filter(
                decision="GENUINE"
            )
            .count()
        )

        suspicious = (
            verifications
            .filter(
                decision="SUSPICIOUS"
            )
            .count()
        )

        fraudulent = (
            verifications
            .filter(
                decision="FAKE"
            )
            .count()
        )

        # ----------------------------------
        # Profile
        # ----------------------------------

        profile = {
            "id": str(
                hr.id
            ),

            "first_name":
                hr.first_name,

            "last_name":
                hr.last_name,

            "email":
                hr.email,

            "phone":
                hr.phone,

            "role":
                hr.role,

            "is_active":
                hr.is_active,

            "profile_image": (
                hr.profile_image.url
                if getattr(
                    hr,
                    "profile_image",
                    None
                )
                else None
            ),

            "created_at":
                hr.created_at,

            "company": (
                {
                    "id":
                        str(company.id),

                    "name":
                        company.name,
                }
                if company
                else None
            ),

            "total_verifications":
                total_verifications,

            "genuine":
                genuine,

            "suspicious":
                suspicious,

            "fraudulent":
                fraudulent,
        }

        return Response(
            {
                "success": True,
                "profile": profile,
            },
            status=status.HTTP_200_OK
        )
        
class UpdateHRProfileView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def put(self, request):

        user = request.user

        # ---------------------------------
        # Only HR can update this profile
        # ---------------------------------

        if user.role != "HR":

            return Response(
                {
                    "success": False,
                    "message":
                        "Only HR users can update their profile."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # ---------------------------------
        # Update text fields
        # ---------------------------------

        user.first_name = request.data.get(
            "first_name",
            user.first_name
        )

        user.last_name = request.data.get(
            "last_name",
            user.last_name
        )

        user.phone = request.data.get(
            "phone",
            user.phone
        )

        # ---------------------------------
        # Profile image
        # ---------------------------------

        profile_image = request.FILES.get(
            "profile_image"
        )

        print(
            "REQUEST FILES:",
            request.FILES
        )

        if profile_image:

            print(
                "PROFILE IMAGE:",
                profile_image.name
            )

            # Delete old image
            if user.profile_image:

                user.profile_image.delete(
                    save=False
                )

            user.profile_image = (
                profile_image
            )

        # ---------------------------------
        # Email intentionally unchanged
        # ---------------------------------

        user.save()

        # ---------------------------------
        # Company
        # ---------------------------------

        company = getattr(
            user,
            "company",
            None
        )

        # ---------------------------------
        # Profile image URL
        # ---------------------------------

        profile_image_url = None

        if user.profile_image:

            profile_image_url = (
                request.build_absolute_uri(
                    user.profile_image.url
                )
            )

        # ---------------------------------
        # Response
        # ---------------------------------

        return Response(
            {
                "success": True,

                "message":
                    "Profile updated successfully.",

                "profile": {

                    "id":
                        str(user.id),

                    "first_name":
                        user.first_name,

                    "last_name":
                        user.last_name,

                    "email":
                        user.email,

                    "phone":
                        user.phone,

                    "role":
                        user.role,

                    "is_active":
                        user.is_active,

                    "profile_image":
                        profile_image_url,

                    "company": (
                        {
                            "id":
                                str(company.id),

                            "name":
                                company.name,
                        }
                        if company
                        else None
                    ),
                },
            },
            status=status.HTTP_200_OK
        )