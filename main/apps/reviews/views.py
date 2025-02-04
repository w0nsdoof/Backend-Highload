from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework import viewsets, status
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs.get("product_pk"))

    def create(self, request, *args, **kwargs):
        product_id = self.kwargs.get("product_pk")
        user = request.user

        if Review.objects.filter(product_id=product_id, user=user).exists():
            return Response(
                {"error": "You have already reviewed this product."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        product_id = self.kwargs.get("product_pk")
        serializer.save(user=self.request.user, product_id=product_id)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            raise PermissionDenied("You cannot edit someone else's review.")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        if review.user != request.user:
            raise PermissionDenied("You cannot delete someone else's review.")
        return super().destroy(request, *args, **kwargs)
