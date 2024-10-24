from django.contrib.auth import login, logout
from django.shortcuts import redirect
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import requests
import base64
import json
from datetime import datetime, timedelta
from .models import SpotifyUser, SpotifyWrap

def spotify_login(request):
    scope = 'user-read-private user-read-email user-top-read user-read-recently-played'
    auth_url = f'https://accounts.spotify.com/authorize'
    params = {
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        'scope': scope
    }
    # Convert params to URL query string
    query_params = '&'.join([f'{k}={v}' for k, v in params.items()])
    return redirect(f'{auth_url}?{query_params}')

def spotify_callback(request):
    code = request.GET.get('code')
    
    # Exchange code for tokens
    auth_header = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    
    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': settings.SPOTIFY_REDIRECT_URI,
        },
        headers={'Authorization': f'Basic {auth_header}'}
    ).json()

    # Get user info from Spotify
    user_data = requests.get(
        'https://api.spotify.com/v1/me',
        headers={'Authorization': f"Bearer {response['access_token']}"}
    ).json()

    # Create or update user
    user, created = SpotifyUser.objects.get_or_create(
        spotify_id=user_data['id'],
        defaults={
            'username': user_data['id'],
            'email': user_data.get('email', ''),
        }
    )
    
    user.spotify_access_token = response['access_token']
    user.spotify_refresh_token = response['refresh_token']
    user.token_expiry = datetime.now() + timedelta(seconds=response['expires_in'])
    user.save()
    
    login(request, user)
    return redirect('dashboard')

@login_required
def refresh_token(request):
    user = request.user
    if not isinstance(user, SpotifyUser):
        return JsonResponse({'error': 'Invalid user type'}, status=400)

    auth_header = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()

    response = requests.post(
        'https://accounts.spotify.com/api/token',
        data={
            'grant_type': 'refresh_token',
            'refresh_token': user.spotify_refresh_token,
        },
        headers={'Authorization': f'Basic {auth_header}'}
    ).json()

    user.spotify_access_token = response['access_token']
    user.token_expiry = datetime.now() + timedelta(seconds=response['expires_in'])
    user.save()

    return JsonResponse({'access_token': response['access_token']})

@login_required
@require_http_methods(['POST'])
def save_wrap(request):
    data = json.loads(request.body)
    wrap = SpotifyWrap.objects.create(
        user=request.user,
        wrap_data=data['wrap_data'],
        title=data['title']
    )
    return JsonResponse({
        'status': 'success',
        'wrap_id': wrap.id
    })

@login_required
def get_wraps(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return JsonResponse({
        'wraps': list(wraps.values('id', 'title', 'created_at', 'wrap_data'))
    })

@login_required
@require_http_methods(['DELETE'])
def delete_wrap(request, wrap_id):
    wrap = SpotifyWrap.objects.get(id=wrap_id, user=request.user)
    wrap.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['POST'])
def delete_account(request):
    request.user.delete()
    logout(request)
    return JsonResponse({'status': 'success'})

@login_required
def dashboard(request):
    wraps = SpotifyWrap.objects.filter(user=request.user)
    return JsonResponse({
        'user': {
            'username': request.user.username,
            'spotify_id': request.user.spotify_id,
        },
        'wraps': list(wraps.values('id', 'title', 'created_at'))
    })