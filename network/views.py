from django.contrib.auth import get_user_model
from django.db.models import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from network.models import Hashtag, Post
from network.permissions import IsOwnerOrReadOnly, IsUserOrReadOnly
from network.serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserFollowSerializer,
    HashtagSerializer,
    PostSerializer,
    PostImageSerializer,
    PostListSerializer,
    PostDetailSerializer,
    PostToggleLikeSerializer,
)


class UserViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated, IsUserOrReadOnly)

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
        return UserDetailSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "email",
                type=OpenApiTypes.STR,
                description="Filter by email contains (ex. ?email=admin)",
            ),
            OpenApiParameter(
                "first_name",
                type=OpenApiTypes.STR,
                description="Filter by first_name contains (ex. ?first_name=bob)",
            ),
            OpenApiParameter(
                "last_name",
                type=OpenApiTypes.STR,
                description="Filter by last_name contains (ex. ?first_name=K)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = (IsAuthenticated,)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    @staticmethod
    def _ids_to_ints(qs):
        """Converts a list of string IDs to a list of integers"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        queryset = (
            Post.objects.select_related("user")
            .prefetch_related("hashtags")
            .annotate(likes=Count("liked_by"))
        )
        if self.action == "list":
            user = get_user_model().objects.get(id=self.request.user.id)
            following_users_id = user.users.values_list("id", flat=True)
            queryset = queryset.filter(
                user__id__in=list(following_users_id) + [user.id]
            )
        hashtags = self.request.query_params.get("hashtags")
        if hashtags:
            queryset = queryset.filter(
                hashtags__id__in=self._ids_to_ints(hashtags)
            ).order_by("id")

        return queryset.distinct().order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        description="upload image to post",
    )
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "hashtags",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by hashtag id (ex. ?hashtags=2,5)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PostToggleLikeView(generics.GenericAPIView):
    serializer_class = PostToggleLikeSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        post = Post.objects.get(id=pk)
        user = self.request.user
        liked_user = post.liked_by.all()
        serializer = self.serializer_class(post, data=request.data)

        if serializer.is_valid():
            if user not in liked_user:
                post.liked_by.add(user)
            else:
                post.liked_by.remove(user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserToggleFollowView(generics.GenericAPIView):
    serializer_class = UserFollowSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        """Endpoint to follow specific user"""
        following_user = get_user_model().objects.get(id=pk)
        current_user = self.request.user
        followers = following_user.followed_by.all()
        serializer = self.get_serializer(following_user, data=request.data)

        if serializer.is_valid():
            if current_user not in followers:
                following_user.followed_by.add(current_user)
            else:
                following_user.followed_by.remove(current_user)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
