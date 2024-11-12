# spotify/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('spotify_app.urls')),  # Make spotify_app the root path
]
