from django.contrib.auth import get_user_model
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from network.serializers import UserListSerializer


class UserViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    serializer_class = UserListSerializer
    queryset = get_user_model().objects.all()
    permission_classes = (IsAuthenticated,)
