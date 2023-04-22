from django.urls import path, include
from rest_framework import routers

from network.views import UserViewSet, HashtagViewSet, PostViewSet

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("hashtags", HashtagViewSet)
router.register("posts", PostViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "network"
