from django.urls import path

from .views.bet_category_views import BetCategoryDetailView, BetCategoryListCreateView
from .views.bet_status_views import BetStatusListView
from .views.sport_views import SportDetailView, SportListCreateView

urlpatterns = [
    path("sports/", SportListCreateView.as_view(), name="sport_list_create"),
    path("sports/<uuid:sport_id>/", SportDetailView.as_view(), name="sport_detail"),
    path("statuses/", BetStatusListView.as_view(), name="bet_status_list"),
    path("categories/", BetCategoryListCreateView.as_view(), name="bet_category_list_create"),
    path("categories/<uuid:category_id>/", BetCategoryDetailView.as_view(), name="bet_category_detail"),
]
