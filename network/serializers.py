from django.contrib.auth import get_user_model
from rest_framework import serializers

from network.models import Hashtag, Post, Comment


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "full_name", "is_staff")
        read_only_fields = ("id", "email", "full_name", "is_staff")


class UserDetailSerializer(serializers.ModelSerializer):
    followers = serializers.SlugRelatedField(
        source="followed_by", many=True, read_only=True, slug_field="email"
    )

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "is_staff",
            "image",
            "bio",
            "followers",
        )

        read_only_fields = ("is_staff",)
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}


class UserFollowSerializer(UserDetailSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "image",
            "bio",
            "followers",
        )
        read_only_fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "image",
            "bio",
        )


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ("id", "name")


class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        source="user", read_only=True, many=False, slug_field="email"
    )

    class Meta:
        model = Comment
        fields = ("id", "content", "author")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        source="user", read_only=True, many=False, slug_field="email"
    )

    class Meta:
        model = Post
        fields = ("id", "title", "content", "hashtags", "image", "created_at", "author")


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("id", "image")


class PostListSerializer(PostSerializer):
    hashtags = HashtagSerializer(read_only=True, many=True)
    likes = serializers.IntegerField(read_only=True)
    comments_amount = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "hashtags",
            "image",
            "created_at",
            "likes",
            "comments_amount",
            "author",
        )
        read_only_fields = ("id", "title", "image", "created_at", "author")


class PostDetailSerializer(PostSerializer):
    hashtags = HashtagSerializer(read_only=True, many=True)
    liked_by = UserListSerializer(many=True, read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "image",
            "created_at",
            "author",
            "liked_by",
            "comments",
        )
        read_only_fields = (
            "id",
            "author",
        )


class PostToggleLikeSerializer(PostDetailSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "image",
            "created_at",
            "author",
            "liked_by",
            "comments",
        )
        read_only_fields = (
            "id",
            "title",
            "content",
            "hashtags",
            "image",
            "created_at",
            "author",
        )
