from django.urls import path

from .views import (
  VerifyCertificateView,
  VerificationStatusView,
  RecentVerificationsView,
  VerificationListView,
  VerificationStatsView,
  VerificationDetailView,
  DeleteVerificationView,
)

urlpatterns = [
    path("verify-certificate/",VerifyCertificateView.as_view()),
    path("status/<uuid:verification_id>/",VerificationStatusView.as_view()),
     path('recent/',RecentVerificationsView.as_view()),
     path("verifications/",VerificationListView.as_view()),
     path('verification/stats/',VerificationStatsView.as_view(),name="verification-stats"),
     path('verification/<uuid:verification_id>/',VerificationDetailView.as_view()),
     path('verification/<uuid:verification_id>/delete/',DeleteVerificationView.as_view),
     
]