from django.contrib import admin

from network.models import Post, Hashtag, Comment

admin.site.register(Hashtag)
admin.site.register(Post)
admin.site.register(Comment)
