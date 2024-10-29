# spotify_app/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'spotify_app/home.html')
