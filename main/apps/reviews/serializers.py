from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ["id", "product", "user", "rating", "comment", "created_at", "updated_at"]
        read_only_fields = ["user", "created_at", "updated_at"]