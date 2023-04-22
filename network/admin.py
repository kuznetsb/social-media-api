from django.contrib import admin

from network.models import Post, Hashtag

admin.site.register(Hashtag)
admin.site.register(Post)
