from django.contrib.auth import get_user_model
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from user.serializers import (
    UserSerializer,
    LogoutSerializer,
    UserImageSerializer,
    MyDetailSerializer,
)


class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UserManageView(generics.RetrieveUpdateAPIView):
    serializer_class = MyDetailSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        user = self.request.user
        return (
            get_user_model()
            .objects.prefetch_related("followed_by", "users")
            .get(id=user.id)
        )


class UploadMyImageView(generics.GenericAPIView):
    serializer_class = UserImageSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user
        serializer = self.serializer_class(user, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
