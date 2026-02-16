from django.urls import path

from .views.login_view import LoginView
from .views.logout_view import LogoutView
from .views.refresh_view import RefreshView
from .views.register_view import RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="user_register"),
    path("login/", LoginView.as_view(), name="user_login"),
    path("refresh/", RefreshView.as_view(), name="user_refresh"),
    path("logout/", LogoutView.as_view(), name="user_logout"),
]
