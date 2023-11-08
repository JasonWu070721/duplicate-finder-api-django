from django.db import models

# Create your models here.


class File(models.Model):
    file_name = models.CharField(max_length=255, blank=True)
    file_size = models.IntegerField(null=True, blank=True)
    file_mtime = models.FloatField(null=True, blank=True)
    file_ctime = models.FloatField(null=True, blank=True)
    file_extension = models.CharField(max_length=255, blank=True)
    file_md5 = models.CharField(max_length=255, null=True, blank=True)
    file_path = models.CharField(max_length=255, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name
