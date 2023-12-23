from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('favorite_videos/', views.favorite_videos, name='favorite_videos'),
    path('remove_favorite/', views.remove_favorite, name='remove_favorite'),
    path('add_to_favorites/<str:video_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/<str:video_id>/', views.remove_from_favorites, name='remove_from_favorites'),
]
