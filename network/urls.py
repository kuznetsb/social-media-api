from django.urls import path, include
from rest_framework import routers

from network.views import (
    UserViewSet,
    HashtagViewSet,
    PostViewSet,
    PostToggleLikeView,
    UserToggleFollowView,
    AddCommentView,
    ManageCommentView,
)

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("hashtags", HashtagViewSet)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<int:pk>/toggle-like/",
        PostToggleLikeView.as_view(),
        name="post_toggle_like",
    ),
    path(
        "users/<int:pk>/toggle-follow/",
        UserToggleFollowView.as_view(),
        name="user_toggle_follow",
    ),
    path(
        "posts/<int:pk>/comment/",
        AddCommentView.as_view(),
        name="post_add_comment",
    ),
    path("comments/<int:pk>/", ManageCommentView.as_view(), name="manage-comment"),
]

app_name = "network"
