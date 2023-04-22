import os
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, User
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


def user_image_file_path(instance, filename):
    _, ext = os.path.splitext(filename)

    email = instance.email.split("@")[0].replace(".", "")

    filename = f"{email}-{uuid.uuid4()}.{ext}"

    return os.path.join("uploads/users/", filename)


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    image = models.ImageField(null=True, upload_to=user_image_file_path, blank=True)
    bio = models.TextField(blank=True)
    followed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="users"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def full_name(self) -> str:
        return self.get_full_name()

    def __str__(self):
        user = f"User: {self.email}"
        if self.first_name and self.last_name:
            user += ", Full name:" + self.get_full_name()
        return user

    def toggle_follow(self, user: User) -> None:
        """Switch following parameter for user"""
        if user in self.followed_by.all():
            self.followed_by.remove(user)
        else:
            self.followed_by.add(user)
