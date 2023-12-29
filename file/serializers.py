from rest_framework import serializers
from file.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            "id",
            "name",
            "size",
            "mtime",
            "ctime",
            "extension",
            "hash_md5",
            "hash_blake2",
            "full_path",
            "created_at",
            "updated_at",
        )
