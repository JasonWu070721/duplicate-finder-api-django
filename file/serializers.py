from rest_framework import serializers
from file.models import File
from file.models import SearchResult


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


class SearchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchResult
        fields = (
            "id",
            "group_id",
            "file_id",
            "full_path",
            "hash_blake2",
            "hash_md5",
            "size",
            "mtime",
            "ctime",
            "extension",
            "created_at",
            "updated_at",
        )
