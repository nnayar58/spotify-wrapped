from django.urls import path
from . import views

urlpatterns = [
    path('auth/spotify/login/', views.spotify_login, name='spotify_login'),
    path('auth/spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('auth/refresh-token/', views.refresh_token, name='refresh_token'),
    path('wrap/save/', views.save_wrap, name='save_wrap'),
    path('wrap/list/', views.get_wraps, name='get_wraps'),
    path('wrap/delete/<int:wrap_id>/', views.delete_wrap, name='delete_wrap'),
    path('account/delete/', views.delete_account, name='delete_account'),
    path('dashboard/', views.dashboard, name='dashboard'),
]