from isodate import parse_duration
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import UserProfile, Video
import requests
import json


def index(request):
    videos = []

    if request.method == 'POST':
        search_url = 'https://www.googleapis.com/youtube/v3/search'
        video_url = 'https://www.googleapis.com/youtube/v3/videos'

        search_params = {
            'part': 'snippet',
            'q': request.POST.get('search', ''),
            'key': settings.YOUTUBE_DATA_API_KEY,
            'maxResults': 9,
            'type': 'video'
        }

        # Use the requests library to send HTTP requests
        r = requests.get(search_url, params=search_params)

        results = r.json().get('items', [])

        video_ids = []
        for result in results:
            video_ids.append(result['id']['videoId'])

        if request.POST.get('submit') == 'lucky' and video_ids:
            return redirect(f'https://www.youtube.com/watch?v={video_ids[0]}')

        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet,contentDetails',
            'id': ','.join(video_ids),
            'maxResults': 9
        }

        r = requests.get(video_url, params=video_params)

        results = r.json().get('items', [])

        for result in results:
            video_data = {
                'title': result['snippet']['title'],
                'id': result['id'],
                'url': f'https://www.youtube.com/watch?v={result["id"]}',
                'duration': int(parse_duration(result['contentDetails']['duration']).total_seconds() // 60),
                'thumbnail': result['snippet']['thumbnails']['high']['url']
            }

            videos.append(video_data)

    context = {
        'videos': videos
    }

    if request.method == 'POST':
        if 'add-to-favorites' in request.POST:
            video_id = request.POST.get('video_id')
            add_to_favorites(request, video_id)
            return JsonResponse({'message': 'Video added to favorites.'})

        if 'remove-from-favorites' in request.POST:
            video_id = request.POST.get('video_id')
            remove_from_favorites(request, video_id)
            return JsonResponse({'message': 'Video removed from favorites.'})

    return render(request, 'search/index.html', context)


def add_to_favorites(request, video_id):
    video_url = f'https://www.googleapis.com/youtube/v3/videos'

    video_params = {
        'key': settings.YOUTUBE_DATA_API_KEY,
        'part': 'snippet,contentDetails',
        'id': video_id,
        'maxResults': 1
    }

    response = requests.get(video_url, params=video_params)

    try:
        response_data = json.loads(response.content)
        video_data = response_data.get('items', [])
    except json.JSONDecodeError:
        return JsonResponse({'message': 'Error adding video to favorites. Invalid API response.'})

    if video_data:
        video_info = video_data[0]['snippet']
        title = video_info['title']
        thumbnail = video_info['thumbnails']['high']['url']
        duration = int(parse_duration(video_data[0]['contentDetails']['duration']).total_seconds() // 60)

        video = Video.objects.create(
            title=title,
            video_id=video_id,
            url=f'https://www.youtube.com/watch?v={video_id}',
            duration=duration,
            thumbnail=thumbnail
        )

        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        user_profile.favorites.add(video)
        user_profile.save()

        return JsonResponse({'message': 'Video added to favorites.'})

    return JsonResponse({'message': 'Error adding video to favorites. Video not found.'})


def remove_from_favorites(request, video_id):
    video = get_object_or_404(Video, video_id=video_id)
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.favorites.remove(video)
    user_profile.save()


def favorite_videos(request):
    user_profile = UserProfile.objects.get(user=request.user)
    favorites = user_profile.favorites.all()

    context = {
        'favorite_videos': favorites
    }

    return render(request, 'search/favorite_videos.html', context)


def remove_favorite(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id')
        remove_from_favorites(request, video_id)
        return JsonResponse({'message': 'Video removed from favorites.'})
