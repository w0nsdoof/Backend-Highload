from django.urls import path
from .views import (
    LoginView, RegisterUserView,
    ForgetPasswordView, ResetPasswordView,
)

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterUserView.as_view(), name='register'),
    path('forgot_password/', ForgetPasswordView.as_view(), name='forgot-password'),
    path('reset_password/<str:uid>/<str:token>/', ResetPasswordView.as_view(), name='reset-password'),
]