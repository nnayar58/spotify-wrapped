# spotify_app/urls.py
from django.urls import path
from . import views

app_name = 'spotify_app'  # Define the namespace

urlpatterns = [
    path('', views.home, name='home'),  # Home page of spotify_app
    path('login/', views.spotify_login, name='spotify_login'),
    path('callback/', views.spotify_callback, name='spotify_callback'),
    path('summary/', views.spotify_summary, name='spotify_summary'),
]
