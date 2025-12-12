from django.urls import path 
from .views import PartyIndex, PartyItemsView

# Every request that hits this router file will start with '/parties/

urlpatterns = [
    path('', PartyIndex.as_view()),
    path('<int:pk>/', PartyItemsView.as_view())
]