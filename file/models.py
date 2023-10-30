from django.db import models

# Create your models here.


class File(models.Model):

    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(blank=False)
    file_mtime = models.FloatField(blank=False)
    file_ctime = models.FloatField(blank=False)
    file_extension = models.CharField(max_length=255, blank=True)
    file_md5 = models.CharField(max_length=255, blank=True)
    file_path = models.CharField(max_length=255, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name
