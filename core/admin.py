from django.contrib import admin
from .models import Profile, Post, Comment, Like
from .models import Message, Conversation

admin.site.register(Message)
admin.site.register(Conversation)

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
