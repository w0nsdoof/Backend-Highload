from django.urls import path
from .views import (
    LoginView, RegisterUserView,
    ForgetPasswordView, ResetPasswordView,
    UserRetrieveView, UserProfileUpdateView
)

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterUserView.as_view(), name='register'),
    path('forgot_password/', ForgetPasswordView.as_view(), name='forgot-password'),
    path('reset_password/<str:uid>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
    
    path('me/', UserRetrieveView.as_view(), name='user-retrieve'),
    path('update_profile', UserProfileUpdateView.as_view(), name='update-profile'),
]