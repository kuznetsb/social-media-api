from django.contrib.auth import get_user_model

from network.serializers import PostSerializer

from celery import shared_task


@shared_task
def create_post(data):
    user_id = data.pop("user_id")
    serializer = PostSerializer(data=data)
    if serializer.is_valid():
        user = get_user_model().objects.get(id=user_id)
        serializer.save(user=user)
        return "Successfully created new post"
    return serializer.errors
