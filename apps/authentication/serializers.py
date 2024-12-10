from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid credentials.")

        user = authenticate(username=user.username, password=password)

        if user:
            if not user.is_active:
                raise serializers.ValidationError("Inactive account.")
            return user

        raise serializers.ValidationError("Invalid credentials.")

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=100)

class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=False, write_only=True)

    def validate(self, data):
        password = data.get('password')
        if not password and password != "GENERATE_RANDOM":
            raise serializers.ValidationError("Password is required or use 'GENERATE_RANDOM' to generate one.")
        return data