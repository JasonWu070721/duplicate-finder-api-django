from rest_framework import serializers
from file.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "file_name",
            "file_size",
            "file_mtime",
            "file_ctime",
            "file_extension",
            "file_md5",
            "file_path",
            "created_at",
            "updated_at",
        )
