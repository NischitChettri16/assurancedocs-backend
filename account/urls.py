from django.urls import path

from .views import ( HRLoginView, CreateHRView,LogoutView, HRDashboardStatsView,HRVerificationListView,RecentHRVerificationView,HRVerificationStatsView,UpdateHRPasswordView,HRProfileView,UpdateHRProfileView)

urlpatterns = [

    path(
        "create-hr/",
        CreateHRView.as_view(),
        name="Create-HR"
    ),
    path("hr-login/",HRLoginView.as_view()),
    path('logout/',LogoutView.as_view()),
    path('hr-dashboard-stats/',HRDashboardStatsView.as_view()),
    path('recent-verifications/',RecentHRVerificationView.as_view()),
    path('hr-verifications/',HRVerificationListView.as_view()),
    path('hr-verification-stats/',HRVerificationStatsView.as_view()),
    path('change-password/',UpdateHRPasswordView.as_view()),
    path('profile/',HRProfileView.as_view()),
    path('profile/update/',UpdateHRProfileView.as_view())

]