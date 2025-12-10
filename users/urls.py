from django.urls import path 
from .views import SignUpView, SignInView


# All requests hitting this router already start with /auth

urlpatterns = [
    path('sign-up/', SignUpView.as_view())
]