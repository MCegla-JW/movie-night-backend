from django.urls import path 
from .views import PartyIndex

# Every request that hits this router file will start with '/parties/

urlpatterns = [
    path('', PartyIndex.as_view())
]