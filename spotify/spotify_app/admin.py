from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SpotifyUser, SpotifyWrap

admin.site.register(SpotifyUser, UserAdmin)
admin.site.register(SpotifyWrap)