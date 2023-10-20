

from file.models import File
from file.serializers import FileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import viewsets, status


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()

    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'id'

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return [IsAuthenticatedOrReadOnly()]

        return super().get_permissions()

    def list(self, request):
        try:
            queryset = File.objects.all()
            serializer = FileSerializer(queryset, many=True)
            return Response(serializer.data)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, id=None, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            file = queryset.get(id=id)
            serializer = self.get_serializer(file)

            return Response(serializer.data)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, id, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            file = queryset.get(id=id)
            request_data = request.data
            serializer = self.get_serializer(file, data=request_data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response(serializer.data)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request",
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, id, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            file = queryset.get(id=id)

            file.delete()
            return Response(status=status.HTTP_200_OK)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)
