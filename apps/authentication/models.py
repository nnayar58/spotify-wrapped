from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SpotifyUser(AbstractUser):
    spotify_id = models.CharField(max_length=200, unique=True, null=True)
    spotify_access_token = models.CharField(max_length=500, null=True)
    spotify_refresh_token = models.CharField(max_length=500, null=True)
    token_expiry = models.DateTimeField(null=True)

class SpotifyWrap(models.Model):
    user = models.ForeignKey(SpotifyUser, on_delete=models.CASCADE, related_name='wraps')
    created_at = models.DateTimeField(default=timezone.now)
    wrap_data = models.JSONField()
    title = models.CharField(max_length=200)

    class Meta:
        ordering = ['-created_at']