from django.urls import path
from . import views

app_name = "spotify_app"  # Ensure this matches the namespace used in your project
urlpatterns = [
    path('', views.home, name='home'),  # Home page route
    path("login/", views.spotify_login, name="spotify_login"),
    path("callback/", views.spotify_callback, name="spotify_callback"),
    path("summary/", views.spotify_summary, name="spotify_summary"),
]
