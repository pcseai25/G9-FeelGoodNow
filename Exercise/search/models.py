from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    favorites = models.ManyToManyField('Video', related_name='users_favorite')

    def __str__(self):
        return self.user.username


class Video(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='videos', blank=True, null=True)
    video_id = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    duration = models.IntegerField()
    thumbnail = models.URLField()
    url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title

