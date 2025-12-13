from django.urls import path 
from .views import PartyIndex, PartyItemsView, PartyJoinView
import uuid

# Every request that hits this router file will start with '/parties/

urlpatterns = [
    path('', PartyIndex.as_view()),
    path('<int:pk>/', PartyItemsView.as_view()),
    path('join/<uuid:join_code>/', PartyJoinView.as_view())
]