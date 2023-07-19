from django.db import models


class Files(models.Model):
    name = models.CharField(max_length=255, null=True)
    size = models.IntegerField(null=True)
    file_mtime = models.DateTimeField(null=True)
    file_ctime = models.DateTimeField(null=True)
    extension = models.CharField(max_length=255, null=True)
    md5 = models.CharField(max_length=255, null=True)
    path = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
