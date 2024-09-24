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


class SearchResult(models.Model):
    group_id = models.IntegerField(null=True, blank=True)
    file_id = models.IntegerField(null=True, blank=True)
    full_path = models.TextField(null=True, blank=True)
    hash_blake2 = models.CharField(max_length=255, null=True, blank=True)
    hash_md5 = models.CharField(max_length=255, null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)
    mtime = models.FloatField(null=True, blank=True)
    ctime = models.FloatField(null=True, blank=True)
    extension = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp of creation
    updated_at = models.DateTimeField(auto_now=True)  # Timestamp of the last update
