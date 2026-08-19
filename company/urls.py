from django.urls import path

from .views import (
    CompanySignupView,
    CompanyLoginView,
    CompanyDashboardView,
    CompanyHRListView,
    CompanyProfileView,
    UpdateCompanyProfileView,
    ChangePasswordView
)

urlpatterns = [

    path(
        "signup/",
        CompanySignupView.as_view(),
        name="company-signup"
    ),

    path(
        "login/",
        CompanyLoginView.as_view(),
        name="company-login"
    ),
    path('dashboard/',CompanyDashboardView.as_view()),
       path(
        "hrs/",
        CompanyHRListView.as_view(),
        name="company-hrs"
    ),
    path('profile/',CompanyProfileView.as_view()),
    path('profile/update/',UpdateCompanyProfileView.as_view()),
    path('change-password/',ChangePasswordView.as_view()),

]