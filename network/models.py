import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Hashtag(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


def post_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)

    filename = f"{slugify(instance.title)}-{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/posts/", filename)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    hashtag = models.ManyToManyField(Hashtag, related_name="posts")
    image = models.ImageField(null=True, upload_to=post_image_file_path, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
