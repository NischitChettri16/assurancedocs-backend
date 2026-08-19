from uuid import uuid4
from pathlib import Path

from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Verification
from .services import process_verification
from threading import Thread
from django.shortcuts import get_object_or_404
from account.authentication import CustomJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import VerificationMessageGenerator
from django.db import transaction


class VerifyCertificateView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def post(self, request):

        file = request.FILES.get(
            "certificate"
        )

        # -----------------------------
        # File Validation
        # -----------------------------

        if not file:

            return Response(
                {
                    "success": False,
                    "message":
                        "Certificate file required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # File Size Validation
        # -----------------------------

        if file.size > 3 * 1024 * 1024:

            return Response(
                {
                    "success": False,
                    "message":
                        "Certificate image must be less than 3MB."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # -----------------------------
        # File Type Validation
        # -----------------------------

        allowed_types = [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/webp",
        ]

        if file.content_type not in allowed_types:

            return Response(
                {
                    "success": False,
                    "message":
                        "Only JPG, PNG and WEBP files are allowed."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            company = request.user.company

            # ---------------------------------
            # Create verification
            # ---------------------------------

            with transaction.atomic():

                verification = (
                    Verification.objects.create(
                        company=company,
                        verified_by=request.user,
                        status="PENDING",
                    )
                )

                # ---------------------------------
                # Save certificate
                # ---------------------------------

                extension = (
                    Path(file.name)
                    .suffix
                    .lower()
                )

                verification.certificate.save(
                    f"{uuid4()}{extension}",
                    file,
                    save=True,
                )

            # ---------------------------------
            # Start background verification
            # ---------------------------------

            Thread(
                target=process_verification,
                args=(verification.id,),
                daemon=True
            ).start()

            print(
                "Starting background verification..."
            )

            return Response(
                {
                    "success": True,
                    "message":
                        "Verification started.",
                    "verification_id":
                        str(
                            verification.id
                        ),
                    "status":
                        verification.status,
                },
                status=status.HTTP_202_ACCEPTED
            )

        except Exception as e:

            return Response(
                {
                    "success": False,
                    "message":
                        str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )     



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Verification

# verification/views.py

class VerificationStatusView(
    APIView
):

    permission_classes = [
        IsAuthenticated
    ]

    def get(
        self,
        request,
        verification_id,
    ):

        try:

            verification = (
                Verification.objects.get(
                    id=verification_id,
                    company=request.user.company,
                )
            )

            result_data = (
                verification.raw_result
            )

            if not result_data:

                result_data = {
                    "platform": {
                        "platform":
                            verification.platform
                    },

                    "fields": {
                        "student_name":
                            verification.student_name,

                        "course_name":
                            verification.course_name,

                        "verification_url":
                            verification.verification_url,
                    },

                    "result": {
                        "score":
                            verification.authenticity_score,

                        "decision":
                            verification.decision,
                    },
                }

            return Response(
                {
                    "success": True,

                    "verification_id": str(
                        verification.id
                    ),

                    "status":
                        verification.status,

                    "progress":
                        verification.progress,

                    "data":
                        result_data,
                }
            )

        except Verification.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message":
                        "Verification not found."
                },
                status=404,
            )


# verification/views.py




class RecentVerificationsView(APIView):

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request):

        company = request.user.company

        verifications = (
            Verification.objects.filter(
                company=company
            )
            .order_by(
                "-created_at"
            )[:20]
        )

        data = []

        for verification in verifications:

            data.append(
                {
                    "id": str(
                        verification.id
                    ),
                    "student_name": (
                        verification.student_name
                    ),
                    "course_name": (
                        verification.course_name
                    ),
                    "platform": (
                        verification.platform
                    ),
                    "decision": (
                        verification.decision
                    ),
                    "score": (
                        verification.authenticity_score
                    ),
                    "status": (
                        verification.status
                    ),
                    "created_at": (
                        verification.created_at
                    ),
                }
            )

        return Response(
            {
                "success": True,
                "count": len(data),
                "results": data,
            }
        )
        



class VerificationListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        company = request.user.company

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

        queryset = (
            Verification.objects.filter(
                company=company
            )
            .select_related(
                "verified_by"
            )
            .order_by(
                "-created_at"
            )
        )

        # -----------------------
        # Search
        # -----------------------

        if search:

            queryset = queryset.filter(
                Q(student_name__icontains=search)
                |
                Q(platform__icontains=search)
                |
                Q(course_name__icontains=search)
                |
                Q(decision__icontains=search)
            )

        # -----------------------
        # Decision Filter
        # -----------------------

        if decision:

            queryset = queryset.filter(
                decision__iexact=decision
            )
        if platform:

            queryset = queryset.filter(
                platform__iexact=platform
            )

        total_records = queryset.count()

        total_pages = (
            (
                total_records
                + page_size
                - 1
            )
            // page_size
        )

        start = (
            page - 1
        ) * page_size

        end = start + page_size

        records = queryset[start:end]

        results = []

        for verification in records:

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

                    "decision":
                        verification.decision,

                    "authenticity_score":
                        verification.authenticity_score,

                    "verified_by":
                        (
                            verification.verified_by.first_name
                            + " "
                            + verification.verified_by.last_name
                        )
                        if verification.verified_by
                        else None,

                    "created_at":
                        verification.created_at,
                }
            )

        return Response(
            {
                "success": True,
                "results": results,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_pages": total_pages,
                    "total_records": total_records,
                    "has_next": page < total_pages,
                    "has_previous": page > 1,
                },
            }
        )



class VerificationStatsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        company = request.user.company

        queryset = Verification.objects.filter(
            company=company
        )

        total_checks = queryset.count()

        genuine_count = queryset.filter(
            decision="GENUINE"
        ).count()

        suspicious_count = queryset.filter(
            decision="SUSPICIOUS"
        ).count()

        fake_count = queryset.filter(
            decision="FAKE"
        ).count()

        return Response(
            {
                "success": True,
                "stats": {
                    "total_checks": total_checks,
                    "genuine": genuine_count,
                    "suspicious": suspicious_count,
                    "fraudulent": fake_count,
                },
            }
        )



class VerificationDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, verification_id):

        company = request.user.company

        verification = get_object_or_404(
            Verification,
            id=verification_id,
            company=company
        )

        raw_result = (
            verification.raw_result or {}
        )

        visual_features = raw_result.get(
            "visual_features",
            {}
        )

        fields = raw_result.get(
            "fields",
            {}
        )

        analysis = (
            VerificationMessageGenerator.generate(
                platform=verification.platform,
                url_valid=verification.url_valid,
                course_similarity=raw_result.get(
                    "course_similarity",
                    0
                ),
                logos=visual_features.get(
                    "logos",
                    []
                ),
                stamps=visual_features.get(
                    "stamps",
                    []
                ),
                signatures=visual_features.get(
                    "signatures",
                    []
                ),
                fields=fields,
                score=verification.authenticity_score,
                decision=verification.decision,
            )
        )

        return Response({
            "success": True,
            "verification": {
                "id": str(
                    verification.id
                ),
                "student_name":
                    verification.student_name,
                "course_name":
                    verification.course_name,
                "issuer":
                    verification.issuer,
                "platform":
                    verification.platform,
                "decision":
                    verification.decision,
                "authenticity_score":
                    verification.authenticity_score,
                "verification_url":
                    verification.verification_url,
                "url_valid":
                    verification.url_valid,
                "status":
                    verification.status,
                "certificate":
                    verification.certificate.url
                    if verification.certificate
                    else None,
                "created_at":
                    verification.created_at,
                "raw_result":
                    raw_result,

                # New analysis section
                "analysis":
                    analysis,
            }
        })
        



class DeleteVerificationView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes=[CustomJWTAuthentication]

    def delete(self, request, verification_id):

        company = request.user.company

        verification = get_object_or_404(
            Verification,
            id=verification_id,
            company=company
        )

        verification.delete()

        return Response(
            {
                "success": True,
                "message": "Verification deleted successfully."
            },
            status=status.HTTP_200_OK
        )