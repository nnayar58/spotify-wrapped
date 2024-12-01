# spotify_app/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(default=timezone.now)
    spotify_user_id = models.CharField(max_length=100, blank=True, null=True)
    access_token = models.CharField(max_length=255, blank=True, null=True)
    refresh_token = models.CharField(max_length=255, blank=True, null=True)
    token_expires = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name}"

from django.contrib.auth.models import User

class SavedWrap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_wraps')
    top_artists = models.JSONField()
    top_genres = models.JSONField()
    top_tracks = models.JSONField()
    total_listening_time = models.IntegerField(default=0)
    peak_listening_day = models.CharField(max_length=100, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wrap saved on {self.created_at}"

class Screenshot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Associate screenshot with a user
    file_path = models.CharField(max_length=255)  # Path to the screenshot file relative to MEDIA_ROOT
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for the screenshot

    def __str__(self):
        return f"{self.user.username} - {self.file_path}"
