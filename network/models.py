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
    content = models.TextField(blank=True)
    hashtags = models.ManyToManyField(Hashtag, related_name="posts", blank=True)
    image = models.ImageField(null=True, upload_to=post_image_file_path, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_posts", blank=True
    )
    schedule = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} post by {self.user} at {self.created_at}"

    def toggle_like(self, user):
        """Toggles the liked state of the post for the given user."""
        if user in self.liked_by.all():
            self.liked_by.remove(user)
        else:
            self.liked_by.add(user)


class Comment(models.Model):
    content = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
