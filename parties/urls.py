from django.urls import path 
from .views import PartyIndex, PartyItemsView, PartyJoinView, PartyMovieIndex, VotesIndexView, CastVotesView, BreakTieView

# Every request that hits this router file will start with '/parties/

urlpatterns = [
    path('', PartyIndex.as_view()),
    path('<int:pk>/', PartyItemsView.as_view()),
    path('<int:pk>/movies/', PartyMovieIndex.as_view()),  # Added /
    path('join/<uuid:join_code>/', PartyJoinView.as_view()),
    path('<int:pk>/votes/', VotesIndexView.as_view()),  # Added /
    path('<int:party_id>/movies/<int:movie_id>/vote/', CastVotesView.as_view()),  # Added /
    path('<int:pk>/break-tie/', BreakTieView.as_view())
]