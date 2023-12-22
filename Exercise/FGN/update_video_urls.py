import requests
from isodate import parse_duration
from django.conf import settings
from .models import Video

def update_video_urls():
    videos = Video.objects.all()

    for video in videos:
        video_id = video.video_id
        video_url = f'https://www.googleapis.com/youtube/v3/videos'

        video_params = {
            'key': settings.YOUTUBE_DATA_API_KEY,
            'part': 'snippet',
            'id': video_id,
            'maxResults': 1
        }

        response = requests.get(video_url, params=video_params)
        response_data = response.json()
        items = response_data.get('items', [])

        if items:
            video_data = items[0]['snippet']
            title = video_data['title']
            thumbnail = video_data['thumbnails']['high']['url']

            video.title = title
            video.url = f'https://www.youtube.com/watch?v={video_id}'
            video.thumbnail = thumbnail
            video.save()

            print(f"Updated video: {video.title}")

        else:
            print(f"Video not found: {video_id}")

    print("URL update completed.")

# Call the function to update the video URLs
update_video_urls()
