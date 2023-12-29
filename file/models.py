from django.db import models

# Create your models here.


class File(models.Model):
    name = models.CharField(max_length=255, blank=True)
    size = models.IntegerField(null=True, blank=True)
    mtime = models.FloatField(null=True, blank=True)
    ctime = models.FloatField(null=True, blank=True)
    extension = models.CharField(max_length=255, blank=True)
    hash_md5 = models.CharField(max_length=255, null=True, blank=True)
    hash_blake2 = models.CharField(max_length=255, null=True, blank=True)
    full_path = models.CharField(max_length=255, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
