from django.urls import path

from authentication.views import *

urlpatterns = [
    # Authentication
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("signin/", SignInView.as_view(), name="user-login-view"),
    path("signup/", SignUpView.as_view(), name="user-signup-view"),
    # OTP
    path("get-otp/", GetOtpView.as_view(), name="get-otp-view"),
    path("verify-otp/", VerifyOtpView.as_view(), name="otp-verify-view"),
    # Password
    path("change-password/", ChangePasswordView.as_view(), name="change-password-view"),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password-view"),
    # Social
    path("linkedin/", LinkedInView.as_view(), name="sso-linkedin"),
    path("linkedin/link/", LinkedinLinkingView.as_view(), name="link-linkedin"),
    # User data
    path("user/", UserView.as_view(), name="user"),
]
