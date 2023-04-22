from django.urls import path, include
from rest_framework import routers

from network.views import UserViewSet, HashtagViewSet

router = routers.DefaultRouter()
router.register("users", UserViewSet)
router.register("hashtags", HashtagViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "network"
