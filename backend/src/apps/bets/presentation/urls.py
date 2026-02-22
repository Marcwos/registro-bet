from django.urls import path

from .views.balance_views import BetHistoryView, DailyBalanceView, TotalBalanceView
from .views.bet_category_views import BetCategoryDetailView, BetCategoryListCreateView
from .views.bet_status_views import BetStatusListView
from .views.bet_views import BetChangeStatusView, BetDetailView, BetListCreateView
from .views.sport_views import SportDetailView, SportListCreateView

urlpatterns = [
    path("sports/", SportListCreateView.as_view(), name="sport_list_create"),
    path("sports/<uuid:sport_id>/", SportDetailView.as_view(), name="sport_detail"),
    path("statuses/", BetStatusListView.as_view(), name="bet_status_list"),
    path("categories/", BetCategoryListCreateView.as_view(), name="bet_category_list_create"),
    path("categories/<uuid:category_id>/", BetCategoryDetailView.as_view(), name="bet_category_detail"),
    path("", BetListCreateView.as_view(), name="bet_list_create"),
    path("<uuid:bet_id>/", BetDetailView.as_view(), name="bet_detail"),
    path("<uuid:bet_id>/status/", BetChangeStatusView.as_view(), name="bet_change_status"),
    path("balance/daily/", DailyBalanceView.as_view(), name="daily_balance"),
    path("balance/total/", TotalBalanceView.as_view(), name="total_balance"),
    path("history/", BetHistoryView.as_view(), name="bet_history"),
]
