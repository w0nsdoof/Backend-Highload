import random, string
import logging

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response

from .security import LoginThrottle,ForgetPasswordThrottle
from .models import User
from .tasks import send_email_task
from .serializers import (
    LoginSerializer, RegisterUserSerializer,
    ForgotPasswordSerializer,ResetPasswordSerializer
)

logger = logging.getLogger(__name__)

class LoginView(GenericAPIView):
    serializer_class = LoginSerializer
    throttle_classes = [LoginThrottle]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"User {user.email} logged in successfully")

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }, status=status.HTTP_200_OK)

class RegisterUserView(GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        logger.info(f"New user registered with email: {serializer.data['email']}")
        
        return Response({
            'message': 'User registered successfully!',
            'user': serializer.data
        }, status=status.HTTP_201_CREATED)

class ForgetPasswordView(GenericAPIView):
    serializer_class = ForgotPasswordSerializer
    throttle_classes = [ForgetPasswordThrottle]
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        if not user:
            logger.warning(f"Password reset attempted for non-existent email: {email}")
            return Response({
                'error': 'No user found with this email.'
            }, status=status.HTTP_404_NOT_FOUND)

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_link = f"{request.scheme}://{request.get_host()}/auth/reset_password/{uid}/{token}"
        send_email_task(
            'Password Reset',
            f"Use this link to reset your password: {reset_link}",
            [user.email],
        )
        
        logger.info(f"Password reset email sent to: {email}")
        return Response({'message': 'Password reset email sent.'}, status=status.HTTP_200_OK)


class ResetPasswordView(GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, uid, token, *args, **kwargs):
        try:
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            logger.error(f"Invalid password reset attempt with uid: {uid}")
            return Response({'error': 'Invalid token or user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            logger.warning(f"Invalid/expired token used for password reset by user: {user.email}")
            return Response({'error': 'Token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Reset password
        new_password = serializer.validated_data.get('password')
        if new_password == "GENERATE_RANDOM":
            new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

        user.set_password(new_password)
        user.save()

        # Send the new password to the user (if generated)
        if "GENERATE_RANDOM" in request.data.values():
            send_email_task(
                'New Password',
                f"Your new password is: {new_password}",
                [user.email],
            )
            logger.info(f"Random password generated and sent to user: {user.email}")
        else:
            logger.info(f"Password reset successful for user: {user.email}")

        return Response({
            'message': 'Password reset successful.'
        }, status=status.HTTP_200_OK)