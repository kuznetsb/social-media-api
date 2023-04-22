from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from network.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserFollowSerializer,
    UserUnfollowSerializer,
)


class UserViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()

        email = self.request.query_params.get("email")
        first_name = self.request.query_params.get("first_name")
        last_name = self.request.query_params.get("last_name")

        if email:
            queryset = queryset.filter(email__icontains=email)
        if first_name:
            queryset = queryset.filter(first_name__icontains=first_name)
        if last_name:
            queryset = queryset.filter(last_name__icontains=last_name)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        if self.action == "retrieve":
            return UserDetailSerializer
        if self.action == "follow":
            return UserFollowSerializer
        if self.action == "unfollow":
            return UserUnfollowSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
        permission_classes=(IsAuthenticated,),
    )
    def follow(self, request, pk=None):
        """Endpoint to follow specific user"""
        following_user = self.get_object()
        current_user = self.request.user
        serializer = self.get_serializer(following_user, data=request.data)
        if serializer.is_valid():
            following_user.followed_by.add(current_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
        permission_classes=(IsAuthenticated,),
    )
    def unfollow(self, request, pk=None):
        """Endpoint to unfollow specific user"""
        following_user = self.get_object()
        current_user = self.request.user
        serializer = self.get_serializer(following_user, data=request.data)
        if serializer.is_valid():
            following_user.followed_by.remove(current_user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
