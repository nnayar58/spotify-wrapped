from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("spotify_app/", include("spotify_app.urls")),  # Confirm this path matches your app
]
