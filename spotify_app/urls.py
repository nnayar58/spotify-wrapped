# spotify_app/urls.py
from django.urls import path
from .views import (  # Explicitly import all views used in urlpatterns
    home,
    signup,
    login_view,
    login_view2,
    logout_view,
    profile_view,
    spotify_login,
    spotify_callback,
    spotify_summary,
    top_genres,
    top_artists,
    top_tracks,
    listening_habits,
    final_summary,
    contact_developers,
    view_feedback,
    feedback_success,
    delete_account,
    view_saved_wraps,
    delete_wrap,
    save_wrapped,
    replay_wrap,
    view_wrap,
    game_artist,
    game_track,
)

app_name = 'spotify_app'  # Define the namespace

urlpatterns = [
    path('', home, name='home'),  # Home page of spotify_app
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('login2/', login_view2, name='login2'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('spotify-login/', spotify_login, name='spotify_login'),
    path('callback/', spotify_callback, name='spotify_callback'),
    path('saved-wraps/', view_saved_wraps, name='view_saved_wraps'),
    path('delete-wrap/<int:wrap_id>/', delete_wrap, name='delete_wrap'),
    path('delete-account/', delete_account, name='delete_account'),
    path('save-wrapped/', save_wrapped, name='save_wrapped'),
    path('view-wrap/<int:wrap_id>/', view_wrap, name='view_wrap'),



    # Flow pages
    path('game_artist/', game_artist, name='game_artist'),
    path('game_track/', game_track, name='game_track'),
    path('top-genres/', top_genres, name='top_genres'),
    path('top-artists/', top_artists, name='top_artists'),
    path('top-tracks/', top_tracks, name='top_tracks'),
    path('listening-habits/', listening_habits, name='listening_habits'),
    path("final-summary/", final_summary, name="final_summary"),
    path("final-summary/<int:wrap_id>/", final_summary, name="final_summary_with_id"),
    path("replay-wrap/<int:wrap_id>/", replay_wrap, name="replay_wrap"),
    path('contact/', contact_developers, name='contact_developers'),
    path('view-feedback/', view_feedback, name='view_feedback'),
    path('feedback_success/', feedback_success, name='feedback_success'),
]
