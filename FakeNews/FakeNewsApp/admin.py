from django.contrib import admin
from .models import Reader, Journalist, Auditor, Article, StakeTransaction, Like, Comment
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Reader)
admin.site.register(Journalist)
admin.site.register(Auditor)
admin.site.register(Article)
admin.site.register(StakeTransaction)
admin.site.register(Like)
admin.site.register(Comment)