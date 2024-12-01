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

import random

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
# Function to get top artists, top songs, genres, listening time, and peak day
def get_top_artists(access_token):
    url = "https://api.spotify.com/v1/me/top/artists?limit=50&time_range=long_term"
    data = get_spotify_data(url, access_token)
    artists = []
    for artist in data.get('items', []):
        artist_info = {
            'name': artist['name'],
            'image_url': artist['images'][0]['url'] if artist['images'] else None,  # Get the first image
        }
        artists.append(artist_info)
    return artists

def get_top_tracks(access_token):
    url = "https://api.spotify.com/v1/me/top/tracks?limit=50&time_range=long_term"  # Last 12 months
    data = get_spotify_data(url, access_token)
    # print("Top Tracks Data:", data)  # Debugging line
    return [
        {
            'name': track.get('name', 'Unknown Track'),  # Use default if 'name' is missing
            'artist': track.get('artists', [{'name': 'Unknown Artist'}])[0].get('name', 'Unknown Artist')
            if track.get('artists') else 'Unknown Artist',  # Handle missing artists
            'image_url': track.get('album', {}).get('images', [{'url': None}])[0].get('url', None)
            if track.get('album', {}).get('images') else None,  # Handle missing images
            'preview_url': track.get('preview_url')  # Get the preview URL, if available
        }
        for track in data.get('items', []) if isinstance(track, dict)  # Ensure each 'track' is a dictionary
    ]


def get_top_genres(access_token):
    genre_mapping = {
        'k-pop girl group': 'k-pop',
        'k-pop boy group': 'k-pop',
        '5th gen k-pop': 'k-pop',
        'pop rock': 'indie',
        'indie pop': 'pop',
        'pop punk': 'pop',
        'dance-pop': 'pop',
        'electropop': 'pop',
        'classic rock': 'rock',
        'hard rock': 'rock',
        'indie rock': 'rock',
        'punk rock': 'rock',
        'alternative rock': 'rock',
        'garage rock': 'rock',
        'psychedelic rock': 'rock',
        'trap': 'hip-hop',
        'gangsta rap': 'hip-hop',
        'underground rap': 'hip-hop',
        'conscious hip-hop': 'hip-hop',
        'rap rock': 'hip-hop',
        'lo-fi rap': 'hip-hop',
        'old school hip-hop': 'hip-hop',
        'house': 'electronic',
        'techno': 'electronic',
        'dubstep': 'electronic',
        'drum and bass': 'electronic',
        'trance': 'electronic',
        'electro house': 'electronic',
        'synthwave': 'electronic',
        'future bass': 'electronic',
        'smooth jazz': 'jazz',
        'vocal jazz': 'jazz',
        'bebop': 'jazz',
        'jazz fusion': 'jazz',
        'soul jazz': 'jazz',
        'electric blues': 'blues',
        'delta blues': 'blues',
        'baroque': 'classical',
        'romantic era': 'classical',
        'modern classical': 'classical',
        'opera': 'classical',
        'chamber music': 'classical',
        'symphony': 'classical',
        'neo soul': 'r&b',
        'contemporary r&b': 'r&b',
        'funk': 'r&b',
        'motown': 'r&b',
        'classic soul': 'r&b',
        'alternative country': 'country',
        'classic country': 'country',
        'country rock': 'country',
        'outlaw country': 'country',
        'country pop': 'country',
        'indie folk': 'folk',
        'americana': 'folk',
        'traditional folk': 'folk',
        'folk rock': 'folk',
        'acoustic': 'folk',
        'dancehall': 'reggae',
        'dub reggae': 'reggae',
        'roots reggae': 'reggae',
        'ska': 'reggae',
        'reggaeton': 'latin',
        'latin pop': 'latin',
        'bachata': 'latin',
        'salsa': 'latin',
        'mariachi': 'latin',
        'cumbia': 'latin',
        'bossa nova': 'latin'
    }

    genre_images = {
        "rock": "https://t.scdn.co/media/derived/rock_9ce79e0a4ef901bbd10494f5b855d3cc_0_0_274_274.jpg",
        "hip-hop": "https://t.scdn.co/images/728ed47fc1674feb95f7ac20236eb6d7.jpeg",
        "country": "https://t.scdn.co/images/a2e0ebe2ebed4566ba1d8236b869241f.jpeg",
        "pop": "https://t.scdn.co/media/derived/pop-274x274_447148649685019f5e2a03a39e78ba52_0_0_274_274.jpg",
        "latin": "https://t.scdn.co/media/derived/latin-274x274_befbbd1fbb8e045491576e317cb16cdf_0_0_274_274.jpg",
        "dance/electronic": "https://t.scdn.co/media/derived/edm-274x274_0ef612604200a9c14995432994455a6d_0_0_274_274.jpg",
        "mood": "https://t.scdn.co/media/original/mood-274x274_976986a31ac8c49794cbdc7246fd5ad7_274x274.jpg",
        "indie": "https://t.scdn.co/images/fe06caf056474bc58862591cd60b57fc.jpeg",
        "r&b": "https://t.scdn.co/media/derived/r-b-274x274_fd56efa72f4f63764b011b68121581d8_0_0_274_274.jpg",
        "christian & gospel": "https://t.scdn.co/media/derived/icon-274x274_5ce6e0f681f0a76f9dcf9270dfd18489_0_0_274_274.jpg",
        "disney": "https://t.scdn.co/images/27922fb7882e4d078c59b29cef4111b9",
        "música mexicana": "https://t.scdn.co/media/derived/latin-274x274_befbbd1fbb8e045491576e317cb16cdf_0_0_274_274.jpg",
        "k-pop": "https://t.scdn.co/images/2078afd91e4d431eb19efc5bee5ab131.jpeg",
        "chill": "https://t.scdn.co/media/derived/chill-274x274_4c46374f007813dd10b37e8d8fd35b4b_0_0_274_274.jpg",
        "decades": "https://t.scdn.co/images/04111a3b810243288d81a539ba03f8d0",
        "love": "https://t.scdn.co/media/derived/romance-274x274_8100794c94847b6d27858bed6fa4d91b_0_0_274_274.jpg",
        "metal": "https://t.scdn.co/media/original/metal_27c921443fd0a5ba95b1b2c2ae654b2b_274x274.jpg",
        "jazz": "https://t.scdn.co/images/568f37f1cab54136939d63bd1f59d40c",
        "classical": "https://t.scdn.co/media/derived/classical-274x274_abf78251ff3d90d2ceaf029253ca7cb4_0_0_274_274.jpg",
        "folk & acoustic": "https://t.scdn.co/images/7fe0f2c9c91f45a3b6bae49d298201a4.jpeg",
        "focus": "https://t.scdn.co/media/original/genre-images-square-274x274_5e50d72b846a198fcd2ca9b3aef5f0c8_274x274.jpg",
        "soul": "https://t.scdn.co/media/derived/soul-274x274_266bc900b35dda8956380cffc73a4d8c_0_0_274_274.jpg",
        "kids & family": "https://t.scdn.co/images/664bb84f7a774e1eadb7c227aed98f3c",
        "gaming": "https://t.scdn.co/images/0d39395309ba47838ef12ce987f19d16.jpeg",
        "anime": "https://t.scdn.co/images/54841f7d6a774ef096477c99c23f0cf1.jpeg",
        "tv & movies": "https://t.scdn.co/images/3be0105e-cc31-4bf2-9958-05568b12370d.jpg",
        "instrumental": "https://t.scdn.co/images/384c2b595a1648aa801837ff99961188",
        "punk": "https://t.scdn.co/media/derived/punk-274x274_f3f1528ea7bbb60a625da13e3315a40b_0_0_274_274.jpg",
        "ambient": "https://t.scdn.co/images/e03887dc75ae48f4bf6503bd894f2b3c",
        "blues": "https://t.scdn.co/images/6fe5cd3ebc8c4db7bb8013152b153505",
        "alternative": "https://t.scdn.co/images/ee9451b3ed474c82b1da8f9b5eafc88f.jpeg",
        "travel": "https://t.scdn.co/media/derived/travel-274x274_1e89cd5b42cf8bd2ff8fc4fb26f2e955_0_0_274_274.jpg",
        "caribbean": "https://t.scdn.co/images/495fadcefe234607b14b2db3381f3f5d.jpeg",
        "afro": "https://t.scdn.co/images/b505b01bbe0e490cbe43b07f16212892.jpeg",
        "bluegrass": "https://t.scdn.co/images/0d39395309ba47838ef12ce987f19d16.jpeg",
    }

    # Fetch top artists from the Spotify API
    url = "https://api.spotify.com/v1/me/top/artists?limit=50&time_range=long_term"
    data = get_spotify_data(url, access_token)

    genres = [genre for artist in data.get('items', []) for genre in artist['genres']]
    unique_genres = sorted(set(genres), key=genres.count, reverse=True)[:15]
    mapped_genres = [genre_mapping.get(genre.lower(), genre) for genre in unique_genres]

    # Remove duplicates while maintaining the order of genres
    seen = set()
    filtered_genres = []
    for genre in mapped_genres:
        if genre not in seen:
            seen.add(genre)
            filtered_genres.append(genre)

    # Ensure exactly 5 genres by filling with fallback genres if necessary
    fallback_genres = list(genre_images.keys())
    while len(filtered_genres) < 5:
        for fallback_genre in fallback_genres:
            if fallback_genre not in filtered_genres:
                filtered_genres.append(fallback_genre)
                if len(filtered_genres) == 5:
                    break

    # Associate images with genres
    genres_with_images = []
    for genre in filtered_genres[:5]:
        genre_lower = genre.lower()
        image_url = genre_images.get(genre_lower, genre_images['indie'])
        genres_with_images.append({
            'name': genre,
            'image_url': image_url
        })

    return genres_with_images

import time
from datetime import datetime, timedelta

def get_total_listening_time(user_profile):
    one_week_ago = datetime.now() - timedelta(days=3)

    # Convert to Unix timestamp (milliseconds)
    one_week_ago_timestamp = int(one_week_ago.timestamp() * 1000)

    # API URL to get recently played tracks
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"

    total_ms = 0
    data = get_spotify_data(url, user_profile)

    # Iterate through the data and filter out tracks played in the past week
    while data:
        for item in data.get('items', []):
            played_at = item['played_at']
            played_at_timestamp = int(datetime.strptime(played_at, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp() * 1000)

            # Only sum the duration if the track was played in the past week
            if played_at_timestamp >= one_week_ago_timestamp:
                total_ms += item['track']['duration_ms']

        # Check if there's another page of results (pagination)
        if 'next' in data and data['next']:
            data = get_spotify_data(data['next'], user_profile)
        else:
            break

    # Convert total milliseconds to hours and minutes
    total_minutes = round(total_ms / (1000 * 60), 2)
    return total_minutes

from dateutil import parser

def get_peak_listening_day(user_profile):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, user_profile)
    days = [parser.isoparse(item['played_at']).strftime('%A') for item in data.get('items', [])]
    return Counter(days).most_common(1)[0][0] if days else None

from collections import Counter
from dateutil import parser

def get_peak_listening_time_of_day(user_profile):
    url = "https://api.spotify.com/v1/me/player/recently-played?limit=50"
    data = get_spotify_data(url, user_profile)
    hours = [parser.isoparse(item['played_at']).hour for item in data.get('items', [])]
    peak_hour = Counter(hours).most_common(1)[0][0] if hours else None

    if peak_hour is not None:
        if peak_hour < 12:
            return "Morning"
        elif peak_hour < 18:
            return "Afternoon"
        else:
            return "Evening"
    return "Evening"


# View to display Spotify summary
def spotify_summary(request):
    user_profile = UserProfile.objects.get(user=request.user)

    top_artists = get_top_artists(user_profile)
    top_tracks = get_top_tracks(user_profile)
    top_genres = get_top_genres(user_profile)
    total_listening_time = get_total_listening_time(user_profile)
    peak_listening_day = get_peak_listening_day(user_profile)
    peak_listening_time_of_day = get_peak_listening_time_of_day(user_profile)

    context = {
        "top_artists": top_artists,
        "top_tracks": top_tracks,
        "top_genres": top_genres,
        "total_listening_time": total_listening_time,
        "peak_listening_day": peak_listening_day,
        "peak_listening_time_of_day": peak_listening_time_of_day,
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

from .models import SavedWrap

def profile_view(request):
    user = request.user
    spotify_connected = hasattr(user, 'userprofile') and user.userprofile.access_token

    # Retrieve saved wraps for the user
    saved_wraps = SavedWrap.objects.filter(user=user)

    return render(request, 'spotify_app/profile.html', {
        'user': user,
        'spotify_connected': spotify_connected,
        'saved_wraps': saved_wraps,  # Pass saved wraps to the template
    })




@login_required
def top_artists(request):
    if request.session.get('is_replay'):
        top_artists = request.session['replay_data']['top_artists']
        context = {'top_artists': top_artists, 'is_replay': True}
        if request.session.get('current_step') == 'top_artists':
            request.session['current_step'] = 'top_tracks'
            return render(request, 'spotify_app/top_artists.html', context)
        else:
            return redirect('spotify_app:top_tracks')
    else:
        # Existing code for fetching new data
        user_profile = UserProfile.objects.get(user=request.user)
        top_artists = get_top_artists(user_profile)
        return render(request, 'spotify_app/top_artists.html', {'top_artists': top_artists})

@login_required
def top_tracks(request):
    if request.session.get('is_replay'):
        top_tracks = request.session['replay_data']['top_tracks']
        context = {'top_tracks': top_tracks, 'is_replay': True}
        if request.session.get('current_step') == 'top_tracks':
            request.session['current_step'] = 'top_genres'
            return render(request, 'spotify_app/top_tracks.html', context)
        else:
            return redirect('spotify_app:top_genres')
    else:
        # Existing code for fetching new data
        user_profile = UserProfile.objects.get(user=request.user)
        top_tracks = get_top_tracks(user_profile)
        return render(request, 'spotify_app/top_tracks.html', {'top_tracks': top_tracks})

@login_required
def top_genres(request):
    if request.session.get('is_replay'):
        top_genres = request.session['replay_data']['top_genres']
        context = {'top_genres': top_genres, 'is_replay': True}
        if request.session.get('current_step') == 'top_genres':
            request.session['current_step'] = 'listening_habits'
            return render(request, 'spotify_app/top_genres.html', context)
        else:
            return redirect('spotify_app:listening_habits')
    else:
        # Existing code for fetching new data
        user_profile = UserProfile.objects.get(user=request.user)
        top_genres = get_top_genres(user_profile)
        return render(request, 'spotify_app/top_genres.html', {'top_genres': top_genres})

@login_required
def listening_habits(request):
    if request.session.get('is_replay'):
        total_listening_time = request.session['replay_data']['total_listening_time']
        peak_listening_day = request.session['replay_data']['peak_listening_day']
        peak_listening_time_of_day = request.session['replay_data']['peak_listening_time_of_day']
        context = {
            'total_listening_time': total_listening_time,
            'peak_listening_day': peak_listening_day,
            'peak_listening_time_of_day': peak_listening_time_of_day,
            'is_replay': True
        }
        if request.session.get('current_step') == 'listening_habits':
            request.session['current_step'] = 'final_summary'
            return render(request, 'spotify_app/listening_habits.html', context)
        else:
            return redirect('spotify_app:final_summary')
    else:
        # Existing code for fetching new data
        user_profile = UserProfile.objects.get(user=request.user)
        total_listening_time = get_total_listening_time(user_profile)
        peak_listening_day = get_peak_listening_day(user_profile)
        peak_listening_time_of_day = get_peak_listening_time_of_day(user_profile)
        return render(request, 'spotify_app/listening_habits.html', {
            'total_listening_time': total_listening_time,
            'peak_listening_day': peak_listening_day,
            'peak_listening_time_of_day': peak_listening_time_of_day,
        })

@login_required
def final_summary(request):
    if request.session.get('is_replay'):
        context = request.session['replay_data']
        context['is_replay'] = True
        # Clear the replay session data
        request.session.pop('replay_data', None)
        request.session.pop('is_replay', None)
        request.session.pop('current_step', None)
    else:
        # Existing code for fetching new data
        user_profile = UserProfile.objects.get(user=request.user)
        context = {
            'top_genres': get_top_genres(user_profile)[:5],
            'top_artists': get_top_artists(user_profile)[:5],
            'top_tracks': get_top_tracks(user_profile)[:5],
            'total_listening_time': get_total_listening_time(user_profile),
            'peak_listening_day': get_peak_listening_day(user_profile),
            'peak_listening_time_of_day': get_peak_listening_time_of_day(user_profile),
            'is_replay': False,
        }
    return render(request, 'spotify_app/final_summary.html', context)


def is_spotify_connected(user):
    try:
        user_profile = UserProfile.objects.get(user=user)
        # Check if access_token and refresh_token are present
        return bool(user_profile.access_token and user_profile.refresh_token)
    except UserProfile.DoesNotExist:
        return False

from django.contrib import messages
def contact_developers(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            # Add a success message
            messages.success(request, 'Thank you for your feedback! Your feedback has been successfully submitted. We appreciate your input.')
            # Don't redirect, just render the same page with the success message
            return render(request, 'spotify_app/contact_developers.html', {'form': form})
    else:
        form = FeedbackForm()

    team_info = [
        {"name": "Rohit Gogi", "role": "Scrum Master", "image": "rohit.png"},
        {"name": "Kelly Zhou", "role": "Product Owner", "image": "kelly.png"},
        {"name": "Shefali Sharma", "role": "Full-Stack Developer", "image": "shefali.jpg"},
        {"name": "Neel Nayar", "role": "Backend Developer", "image": "neel.png"},
        {"name": "Anh-Duy Ha", "role": "Frontend Developer", "image": "andy.png"},
    ]
    return render(request, 'spotify_app/contact_developers.html', {'form': form, 'team_info': team_info})

def view_feedback(request):
    feedback_list = Feedback.objects.all()
    if request.method == 'POST' and 'clear_all' in request.POST:
        Feedback.objects.all().delete()  # Delete all feedback
        return redirect('spotify_app:view_feedback')  # Redirect to the same page to refresh the list
    return render(request, 'spotify_app/view_feedback.html', {'feedback_list': feedback_list})


from django.shortcuts import render, redirect, get_object_or_404
from .models import SavedWrap

@login_required
def view_saved_wraps(request):
    saved_wraps = SavedWrap.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'spotify_app/saved_wraps.html', {'saved_wraps': saved_wraps})

def delete_wrap(request, wrap_id):
    saved_wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    saved_wrap.delete()
    return redirect('spotify_app:view_saved_wraps')

from django.contrib.auth.models import User
from django.contrib.auth import logout

def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('spotify_app:home')
    return render(request, 'spotify_app/delete_account.html')

from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from .models import SavedWrap
from django.core.serializers.json import DjangoJSONEncoder  # Add this line
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

@login_required
def save_wrapped(request):
    if request.method == "POST":
        # Retrieve wrap data from the session
        user = request.user
        wrap_data = request.session.get("current_wrap_data")
        print(request.POST)
        print(wrap_data)
        if not wrap_data:
            return JsonResponse({"error": "No wrap data to save"}, status=400)

        # Check if the wrap is already saved
        try:
            SavedWrap.objects.get(
                user=user,
                top_artists=json.dumps(wrap_data["top_artists"]),
                top_genres=json.dumps(wrap_data["top_genres"]),
                top_tracks=json.dumps(wrap_data["top_tracks"]),
                total_listening_time=wrap_data["total_listening_time"],
                peak_listening_day=wrap_data["peak_listening_day"],
            )
            return JsonResponse({"error": "This wrap is already saved"}, status=400)
        except ObjectDoesNotExist:
            # Save the wrap
            SavedWrap.objects.create(
                user=user,
                top_artists=json.dumps(wrap_data["top_artists"]),
                top_genres=json.dumps(wrap_data["top_genres"]),
                top_tracks=json.dumps(wrap_data["top_tracks"]),
                total_listening_time=wrap_data["total_listening_time"],
                peak_listening_day=wrap_data["peak_listening_day"],
            )
            return redirect("spotify_app:view_saved_wraps")
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)



@login_required
def replay_wrap(request, wrap_id):
    try:
        saved_wrap = SavedWrap.objects.get(id=wrap_id, user=request.user)
        # Load saved data into the session for replay
        request.session['replay_data'] = {
            'top_genres': json.loads(saved_wrap.top_genres),
            'top_artists': json.loads(saved_wrap.top_artists),
            'top_tracks': json.loads(saved_wrap.top_tracks),
            'total_listening_time': saved_wrap.total_listening_time,
            'peak_listening_day': saved_wrap.peak_listening_day,
        }
        request.session['is_replay'] = True
        request.session['current_step'] = 'top_artists'  # Start with top artists
        return redirect('spotify_app:top_artists')
    except SavedWrap.DoesNotExist:
        return redirect('spotify_app:view_saved_wraps')
from django.shortcuts import get_object_or_404

@login_required
def view_wrap(request, wrap_id):
    saved_wrap = get_object_or_404(SavedWrap, id=wrap_id, user=request.user)
    context = {
        'top_artists': json.loads(saved_wrap.top_artists),
        'top_tracks': json.loads(saved_wrap.top_tracks),
        'top_genres': json.loads(saved_wrap.top_genres),
        'total_listening_time': saved_wrap.total_listening_time,
        'peak_listening_day': saved_wrap.peak_listening_day,
    }
    return render(request, 'spotify_app/view_wrap.html', context)

# views.py
from datetime import datetime
from django.shortcuts import render

def base_view(request):
    # For testing, set a specific date (e.g., Halloween)
    test_date = datetime(2025, 10, 31)  # You can change this for testing purposes

    current_month = test_date.month  # Use the test date
    current_day = test_date.day

    # Set the theme based on the date
    if current_month == 10 and current_day == 31:
        theme = 'halloween'
    elif current_month == 12 and current_day == 25:
        theme = 'christmas'
    else:
        theme = 'base'

    # Pass the theme to the template
    return render(request, 'base.html', {'theme': theme})

from random import sample
@login_required
def game_artist(request):
    user_profile = UserProfile.objects.get(user=request.user)  # Get the user's profile
    top_artists = get_top_artists(user_profile)  # Fetch top artists

    # Ensure there are at least 5 artists to choose from
    if len(top_artists) >= 5:
        # Exclude the top artist (the first one in the list) from the shuffle
        remaining_artists = top_artists[1:25]  # Get the next artists, excluding the top artist

        # Shuffle the remaining 14 artists
        shuffled_artists = random.sample(remaining_artists, len(remaining_artists))  # Shuffle the remaining artists

        # Take the first 4 artists from the shuffled list
        artists_to_show = shuffled_artists[:4]

        # Add the top artist as the 5th choice
        artists_to_show.append(top_artists[0])  # Add the top artist to the list

        # Shuffle the final list to randomize position
        random.shuffle(artists_to_show)
    else:
        artists_to_show = top_artists  # If there are fewer than 5 artists, just show them all

    return render(request, 'spotify_app/game_artist.html', {'top_artists': top_artists, 'shuffled_artists': artists_to_show})

import random
@login_required
def game_track(request):
    user_profile = UserProfile.objects.get(user=request.user)  # Get the user's profile
    
    top_tracks = get_top_tracks(user_profile)  # Fetch top tracks
    # print("Length of Top Tracks: ", len(top_tracks))
    # Ensure there are at least 5 tracks to select from
    if len(top_tracks) >= 5:
        # Randomly select one track from the top 6-30 as the "correct track"
        correct_track = random.choice(top_tracks[5:20])

        # Exclude the correct track from the remaining pool
        remaining_tracks = [track for track in top_tracks if track != correct_track]

        # Shuffle the remaining tracks and select 4 others
        shuffled_tracks = random.sample(remaining_tracks, min(len(remaining_tracks), 4))

        # Combine the correct track with the shuffled tracks
        tracks_to_show = shuffled_tracks + [correct_track]
        random.shuffle(tracks_to_show)  # Randomize the display order
    else:
        correct_track = top_tracks[0] if top_tracks else None  # Default to the top track
        tracks_to_show = top_tracks  # If fewer than 5 tracks, just show all tracks

    return render(request, 'spotify_app/game_track.html', {
        'top_tracks': top_tracks,
        'shuffled_track': tracks_to_show,
        'correct_track': correct_track
    })

from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Screenshot
import os
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@login_required
def save_screenshot(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Append the current date and username to the file name
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        original_name, extension = os.path.splitext(image.name)
        new_name = f"{request.user.username}_{original_name}_{current_date}{extension}"

        # Save the file with the new name
        file_path = os.path.join("media/screenshots", new_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)  # Ensure the directory exists

        with open(file_path, "wb+") as destination:
            for chunk in image.chunks():
                destination.write(chunk)

        # Save the screenshot in the database
        relative_url = os.path.join(settings.MEDIA_URL, 'screenshots', new_name)
        Screenshot.objects.create(user=request.user, file_path=relative_url)

        return JsonResponse({"success": True, "file_path": relative_url})

    return JsonResponse({"success": False, "error": "Invalid request."})



@login_required
def my_wraps_view(request):
    # Fetch user profile data
    user_profile = UserProfile.objects.get(user=request.user)

    # Assuming `get_top_artists` is a function that returns the top 5 artists for the user
    top_artists = get_top_artists(user_profile)[:5]  # Limit to top 5 artists
    top_tracks = get_top_tracks(user_profile)[:5]  # Limit to top 5 artists
    top_genres = get_top_genres(user_profile)[:5]  # Limit to top 5 artists



# Fetch other data as needed (like screenshots)
    screenshots = Screenshot.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'screenshots': screenshots,
        'top_artists': top_artists,  # Add top artists to the context
        'top_tracks': top_tracks,  # Add top artists to the context
        'top_genres': top_genres,
    }

    return render(request, 'spotify_app/my_wraps.html', context)


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Screenshot

@login_required
def clear_all_wraps(request):
    if request.method == "POST":
        # Delete all screenshots for the current user
        Screenshot.objects.filter(user=request.user).delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request."})

from django.http import JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Screenshot

@login_required
@csrf_exempt
def delete_wrap(request, screenshot_id):
    if request.method == "POST":
        screenshot = get_object_or_404(Screenshot, id=screenshot_id, user=request.user)
        screenshot.delete()
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"success": False, "error": "Invalid request method."}, status=400)

