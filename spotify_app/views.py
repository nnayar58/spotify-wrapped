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
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile

from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignUpForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .forms import FeedbackForm
from .models import Feedback


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

    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token')
    expires_in = token_info.get('expires_in')
    token_expires = timezone.now() + timedelta(seconds=expires_in)

    # Get Spotify user ID
    user_info_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    user_info_response = requests.get(user_info_url, headers=headers)
    user_info = user_info_response.json()
    spotify_user_id = user_info.get('id')

    # Update UserProfile
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    user_profile.spotify_user_id = spotify_user_id
    user_profile.access_token = access_token
    user_profile.refresh_token = refresh_token
    user_profile.token_expires = token_expires
    user_profile.save()

    return redirect("spotify_app:top_genres")


def refresh_access_token(user_profile):
    token_url = "https://accounts.spotify.com/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": user_profile.refresh_token,
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    }
    response = requests.post(token_url, data=data)
    token_info = response.json()

    # Update the access token and expiration time
    user_profile.access_token = token_info.get('access_token')
    expires_in = token_info.get('expires_in')
    user_profile.token_expires = timezone.now() + timedelta(seconds=expires_in)
    user_profile.save()

def get_spotify_data(url, user_profile):
    # Refresh the access token if it has expired
    if timezone.now() >= user_profile.token_expires:
        refresh_access_token(user_profile)

    headers = {"Authorization": f"Bearer {user_profile.access_token}"}
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print("Error fetching data:", e)
        data = {}

    return data




# Function to get top artists, top songs, genres, listening time, and peak day
def get_top_artists(user_profile):
    url = "https://api.spotify.com/v1/me/top/artists?limit=5&time_range=long_term"
    data = get_spotify_data(url, user_profile)
    print("Top Artists Data:", data)  # Debugging line
    return [artist['name'] for artist in data.get('items', [])]

def get_top_tracks(user_profile):
    url = "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term"
    data = get_spotify_data(url, user_profile)
    print("Top Tracks Data:", data)  # Debugging line
    return [track['name'] for track in data.get('items', [])]

def get_top_genres(user_profile):
    url = "https://api.spotify.com/v1/me/top/artists?limit=50&time_range=long_term"
    data = get_spotify_data(url, user_profile)
    genres = [genre for artist in data.get('items', []) for genre in artist['genres']]
    return sorted(set(genres), key=genres.count, reverse=True)[:5]

def get_total_listening_time(user_profile):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, user_profile)
    total_ms = sum(item['track']['duration_ms'] for item in data.get('items', []))
    total_hours = round(total_ms / (1000 * 60 * 60), 2)
    return total_hours

from dateutil import parser

def get_peak_listening_day(user_profile):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, user_profile)
    days = [parser.isoparse(item['played_at']).strftime('%A') for item in data.get('items', [])]
    return Counter(days).most_common(1)[0][0] if days else None



# View to display Spotify summary
def spotify_summary(request):
    user_profile = UserProfile.objects.get(user=request.user)

    top_artists = get_top_artists(user_profile)
    top_tracks = get_top_tracks(user_profile)
    top_genres = get_top_genres(user_profile)
    total_listening_time = get_total_listening_time(user_profile)
    peak_listening_day = get_peak_listening_day(user_profile)

    context = {
        "top_artists": top_artists,
        "top_tracks": top_tracks,
        "top_genres": top_genres,
        "total_listening_time": total_listening_time,
        "peak_listening_day": peak_listening_day,
    }

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
    spotify_connected = is_spotify_connected(user)

    context = {
        'user': user,
        'spotify_connected': spotify_connected,
        'date_joined': user.date_joined,
    }

    # Do not fetch top artists, tracks, or genres here to avoid spoilers

    return render(request, 'spotify_app/profile.html', context)



# Top Genres Page
@login_required
def top_genres(request):
    user_profile = UserProfile.objects.get(user=request.user)
    top_genres = get_top_genres(user_profile)
    return render(request, 'spotify_app/top_genres.html', {'top_genres': top_genres})

@login_required
def top_artists(request):
    user_profile = UserProfile.objects.get(user=request.user)
    top_artists = get_top_artists(user_profile)
    return render(request, 'spotify_app/top_artists.html', {'top_artists': top_artists})

@login_required
def top_tracks(request):
    user_profile = UserProfile.objects.get(user=request.user)
    top_tracks = get_top_tracks(user_profile)
    return render(request, 'spotify_app/top_tracks.html', {'top_tracks': top_tracks})

@login_required
def listening_habits(request):
    user_profile = UserProfile.objects.get(user=request.user)
    total_listening_time = get_total_listening_time(user_profile)
    peak_listening_day = get_peak_listening_day(user_profile)
    return render(request, 'spotify_app/listening_habits.html', {
        'total_listening_time': total_listening_time,
        'peak_listening_day': peak_listening_day,
    })

# Final Summary Page
@login_required
def final_summary(request):
    user_profile = UserProfile.objects.get(user=request.user)

    context = {
        "top_artists": get_top_artists(user_profile),
        "top_tracks": get_top_tracks(user_profile),
        "top_genres": get_top_genres(user_profile),
        "total_listening_time": get_total_listening_time(user_profile),
        "peak_listening_day": get_peak_listening_day(user_profile),
    }
    return render(request, 'spotify_app/final_summary.html', context)

def is_spotify_connected(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        # Check if access_token and refresh_token are present
        return bool(user_profile.access_token and user_profile.refresh_token)
    except UserProfile.DoesNotExist:
        return False

def contact_developers(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('spotify_app:feedback_success')  # Create a success page or message
    else:
        form = FeedbackForm()
    team_info = [
        {"name": "Rohit Gogi", "role": "Scrum Master"},
        {"name": "Kelly Zhou", "role": "Product Owner"},
        {"name": "Shefali Sharma", "role": "Full-Stack Developer"},
        {"name": "Neel Nayar", "role": "Backend Developer"},
        {"name": "Anh-Duy Ha", "role": "Frontend Developer"},
    ]
    return render(request, 'spotify_app/contact_developers.html', {'form': form, 'team_info': team_info})


def view_feedback(request):
    feedback_list = Feedback.objects.all()
    if request.method == 'POST' and 'clear_all' in request.POST:
        Feedback.objects.all().delete()  # Delete all feedback
        return redirect('spotify_app:view_feedback')  # Redirect to the same page to refresh the list
    return render(request, 'spotify_app/view_feedback.html', {'feedback_list': feedback_list})


def feedback_success(request):
    return render(request, 'spotify_app/feedback_success.html')
