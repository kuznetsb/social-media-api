import datetime

import pytz
from django.contrib.auth import get_user_model
from django.db.models import Count
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from network.models import Hashtag, Post, Comment
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
    CommentSerializer,
    CommentDetailSerializer,
)
from network.tasks import create_post


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
            .prefetch_related("comments__user")
            .annotate(likes=Count("liked_by"), comments_amount=Count("comments"))
        )
        if self.action == "see_my_posts":
            user = get_user_model().objects.get(id=self.request.user.id)
            queryset = queryset.filter(user__id__in=[user.id])
        if self.action == "see_following_users_posts":
            user = get_user_model().objects.get(id=self.request.user.id)
            following_users = user.users.all()
            queryset = queryset.filter(user__in=following_users)
        if self.action == "see_liked_posts":
            user = get_user_model().objects.get(id=self.request.user.id)
            queryset = queryset.filter(liked_by__id__in=[user.id])

        hashtags = self.request.query_params.get("hashtags")
        if hashtags:
            queryset = queryset.filter(
                hashtags__id__in=self._ids_to_ints(hashtags)
            ).order_by("id")

        return queryset.distinct().order_by("-created_at")

    def get_serializer_class(self):
        if self.action in (
            "list",
            "see_liked_posts",
            "see_my_posts",
            "see_following_users_posts",
        ):
            return PostListSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "upload_image":
            return PostImageSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        schedule = self.request.data.get("schedule")
        if schedule:
            time_obj = datetime.datetime.strptime(schedule, "%Y-%m-%dT%H:%M")
            time_now = timezone.datetime.now()
            if time_now < time_obj and serializer.is_valid():
                time_obj = datetime.datetime.strptime(schedule, "%Y-%m-%dT%H:%M")
                tz = timezone.get_current_timezone()
                time_aware = timezone.make_aware(time_obj, timezone=tz)
                data = self.request.data.copy()
                data["user_id"] = self.request.user.id
                create_post.apply_async(
                    args=[data],
                    eta=time_aware,
                )
                return Response(
                    {"message": "Post scheduled successfully."},
                    status=status.HTTP_200_OK,
                )
        return super().create(request, *args, **kwargs)

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

    @action(
        methods=["GET"],
        detail=False,
        url_path="liked",
        description="see posts your liked",
    )
    def see_liked_posts(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="my",
        description="see your posts only",
    )
    def see_my_posts(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["GET"],
        detail=False,
        url_path="following",
        description="see following users posts",
    )
    def see_following_users_posts(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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
        """Endpoint to like or dislike specific post"""
        post = Post.objects.get(id=pk)
        user = self.request.user
        serializer = self.serializer_class(post, data=request.data)

        if serializer.is_valid():
            post.toggle_like(user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserToggleFollowView(generics.GenericAPIView):
    serializer_class = UserFollowSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        """Endpoint to follow or unfollow specific user"""
        following_user = get_user_model().objects.get(id=pk)
        current_user = self.request.user
        if following_user == current_user:
            return Response(
                {"detail": "forbidden to follow yourself"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(following_user, data=request.data)

        if serializer.is_valid():
            following_user.toggle_follow(current_user)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddCommentView(generics.GenericAPIView):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk=None):
        """Endpoint to add comment to specific post"""
        post = Post.objects.get(id=pk)
        user = self.request.user
        serializer = self.get_serializer(data=self.request.data)

        if serializer.is_valid():
            serializer.save(user=user, post=post)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManageCommentView(generics.RetrieveUpdateDestroyAPIView):
    """Endpoint to edit or delete specific comment"""

    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)
