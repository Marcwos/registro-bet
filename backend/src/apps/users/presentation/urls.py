from django.urls import path

from .views.change_password_view import ChangePasswordView
from .views.login_view import LoginView
from .views.logout_view import LogoutView
from .views.refresh_view import RefreshView
from .views.register_view import RegisterView
from .views.reset_password_view import ResetPasswordView
from .views.send_password_recovery_view import SendPasswordRecoveryView
from .views.send_verification_email_view import SendVerificationEmailView
from .views.verify_email_view import VerifyEmailView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user_register"),
    path("login/", LoginView.as_view(), name="user_login"),
    path("refresh/", RefreshView.as_view(), name="user_refresh"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
    path("send-verification/", SendVerificationEmailView.as_view(), name="user_send_verification"),
    path("verify-email/", VerifyEmailView.as_view(), name="user_verify_email"),
    path("recover-password/", SendPasswordRecoveryView.as_view(), name="user_recover_password"),
    path("reset-password/", ResetPasswordView.as_view(), name="user_reset_password"),
    path("change-password/", ChangePasswordView.as_view(), name="user_change_password"),
]
