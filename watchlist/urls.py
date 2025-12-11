from django.urls import path
from .views import WatchlistItemsView, WatchlistIndex

# Every request that hits this router file will start with '/watchlist/'

urlpatterns = [
    path('', WatchlistIndex.as_view()),
    path('<int:pk>/', WatchlistItemsView.as_view())
]
