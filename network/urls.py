from django.urls import path, include
from rest_framework import routers

from network.views import UserViewSet, HashtagViewSet, PostViewSet, PostToggleLikeView

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
]

app_name = "network"
