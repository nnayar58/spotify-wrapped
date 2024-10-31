# spotify_app/urls.py
from django.urls import path
from . import views

app_name = 'spotify_app'  # Define the namespace

urlpatterns = [
    path('', views.home, name='home'),  # Home page of spotify_app
    path('login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('summary/', views.spotify_summary, name='spotify_summary'),

   # Flow pages
    path('top-genres/', views.top_genres, name='top_genres'),
    path('top-artists/', views.top_artists, name='top_artists'),
    path('top-tracks/', views.top_tracks, name='top_tracks'),
    path('listening-habits/', views.listening_habits, name='listening_habits'),
    path('final-summary/', views.final_summary, name='final_summary'),
]
