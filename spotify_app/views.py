# spotify_app/views.py
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
import urllib.parse
import requests
from django.shortcuts import redirect
from django.conf import settings
import urllib.parse
import requests
from django.shortcuts import render
from django.shortcuts import redirect, render
from django.conf import settings
import urllib.parse
import requests
from collections import Counter
from datetime import datetime

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth import logout

def home(request):
    return render(request, 'spotify_app/home.html')

# Spotify Login Redirect
def spotify_login(request):

    auth_url = "https://accounts.spotify.com/authorize"
    params = {
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "response_type": "code",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "scope": "user-top-read user-read-recently-played user-read-playback-position"
    }
    url = f"{auth_url}?{urllib.parse.urlencode(params)}"
    return redirect(url)

# Spotify Callback to Handle OAuth Redirect
def spotify_callback(request):
    code = request.GET.get('code')
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()
    request.session['access_token'] = token_info['access_token']
    return redirect("spotify_app:spotify_summary")

# Helper function to get Spotify data
def get_spotify_data(url, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

# Function to get top artists, top songs, genres, listening time, and peak day
def get_top_artists(access_token):
    url = "https://api.spotify.com/v1/me/top/artists?limit=5&time_range=long_term"
    data = get_spotify_data(url, access_token)
    print("Top Artists Data:", data)  # Debugging line
    return [artist['name'] for artist in data.get('items', [])]


def get_top_tracks(access_token):
    url = "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term"  # Last 12 months
    data = get_spotify_data(url, access_token)
    print("Top Tracks Data:", data)  # Debugging line
    return [track['name'] for track in data.get('items', [])]

def get_top_genres(access_token):
    url = "https://api.spotify.com/v1/me/top/artists?limit=50&time_range=long_term"  # Last 12 months
    data = get_spotify_data(url, access_token)
    genres = [genre for artist in data.get('items', []) for genre in artist['genres']]
    return sorted(set(genres), key=genres.count, reverse=True)[:5]


def get_total_listening_time(access_token):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, access_token)
    total_ms = sum(item['track']['duration_ms'] for item in data.get('items', []))
    total_hours = round(total_ms / (1000 * 60 * 60), 2)
    return total_hours

from dateutil import parser

def get_peak_listening_day(access_token):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, access_token)

    # Use dateutil's parser to handle the ISO 8601 format
    days = [parser.isoparse(item['played_at']).strftime('%A') for item in data.get('items', [])]
    
    return Counter(days).most_common(1)[0][0] if days else None



# View to display Spotify summary
def spotify_summary(request):
    access_token = request.session.get('access_token')
    if not access_token:
        return redirect("spotify_app:spotify_login")
    
    top_artists = get_top_artists(access_token)
    top_tracks = get_top_tracks(access_token)
    top_genres = get_top_genres(access_token)
    total_listening_time = get_total_listening_time(access_token)
    peak_listening_day = get_peak_listening_day(access_token)

    context = {
        "top_artists": top_artists,
        "top_tracks": top_tracks,
        "top_genres": top_genres,
        "total_listening_time": total_listening_time,
        "peak_listening_day": peak_listening_day,
    }

    # Check for empty results
    if not top_artists:
        context["no_top_artists"] = "You don't have any top artists."
    if not top_tracks:
        context["no_top_tracks"] = "You don't have any top tracks."
    if not top_genres:
        context["no_top_genres"] = "You don't have any top genres."

    return render(request, 'spotify_app/spotify_summary.html', context)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('spotify_app:home')
    else:
        form = SignUpForm()
    return render(request, 'spotify_app/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('spotify_app:home')
    else:
        form = AuthenticationForm()
    return render(request, 'spotify_app/login.html', {'form': form})

def login_view2(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('spotify_app:profile')  # Changed to redirect to profile
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'spotify_app/login2.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('spotify_app:home')

from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    spotify_connected = 'access_token' in request.session
    
    context = {
        'user': user,
        'spotify_connected': spotify_connected,
        'date_joined': user.date_joined,
    }
    
    if spotify_connected:
        # Get some Spotify data for the profile if available
        access_token = request.session['access_token']
        try:
            top_artists = get_top_artists(access_token)[:3]  # Get top 3 artists
            top_tracks = get_top_tracks(access_token)[:3]    # Get top 3 tracks
            top_genres = get_top_genres(access_token)[:3]    # Get top 3 genres
            
            context.update({
                'top_artists': top_artists,
                'top_tracks': top_tracks,
                'top_genres': top_genres,
            })
        except:
            pass  # Handle any API errors gracefully
            
    return render(request, 'spotify_app/profile.html', context)