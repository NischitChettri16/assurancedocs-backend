from rest_framework.response import Response

from rest_framework_simplejwt.tokens import (
    RefreshToken
)

from django.conf import settings


def create_auth_response(
    user,
    message="Login Successful.",
    status_code=200,
):
    # ----------------------------------
    # Generate JWT tokens
    # ----------------------------------

    refresh = (
        RefreshToken.for_user(
            user
        )
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
                message,

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

        status=status_code,
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