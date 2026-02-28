from django.urls import include, path

urlpatterns = [
    path("users/", include("src.apps.users.presentation.urls")),
    path("bets/", include("src.apps.bets.presentation.urls")),
    path("admin/", include("src.apps.audit.presentation.urls")),
]
