from django.http import JsonResponse
from django.urls import include, path
from django.views.decorators.http import require_GET


@require_GET
def health_check(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("users/", include("src.apps.users.presentation.urls")),
    path("bets/", include("src.apps.bets.presentation.urls")),
    path("admin/", include("src.apps.audit.presentation.urls")),
]
