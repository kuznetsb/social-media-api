from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from user.views import UserCreateView, UserManageView, LogoutView

urlpatterns = [
    path("register/", UserCreateView.as_view(), name="create_user"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", UserManageView.as_view(), name="manage_user"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
]

app_name = "user"
