from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "full_name", "is_staff")
        read_only_fields = ("id", "email", "full_name", "is_staff")


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "email", "first_name", "last_name", "is_staff", "image", "bio")
        read_only_fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "image",
            "bio",
        )


class UserFollowSerializer(UserDetailSerializer):
    pass


class UserUnfollowSerializer(UserDetailSerializer):
    pass
