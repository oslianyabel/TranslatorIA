from django.db import models

class Video_up(models.Model):
    title = models.CharField(max_length=255, blank=True)
    video = models.FileField(upload_to='uploaded_videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class File(models.Model):
    existingPath = models.CharField(max_length=300)
    name = models.CharField(max_length=100)
    eof = models.BooleanField()