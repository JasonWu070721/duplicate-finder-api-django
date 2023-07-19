from django.contrib.auth.models import User, Group
from files.models import Files
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class FileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Files
        fields = ['name', 'extension', 'size',
                  'path', 'file_mtime', 'file_ctime', 'md5']
