from django.urls import path
from .views import MoviesView

# Every request that hits this router file will start with '/movies/'

urlpatterns = [
    path('', MoviesView.as_view())
]

