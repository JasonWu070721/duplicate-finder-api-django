

from file.models import File
from file.serializers import FileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework import viewsets, status
from file.tasks import file_init
from celery.result import AsyncResult


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()

    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'delete']
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action == 'retrieve' or self.action == 'list':
            return [IsAuthenticatedOrReadOnly()]

        return super().get_permissions()

    @action(detail=False, methods=['GET'], url_path=r'search-status')
    def search_status(self, request, pk=None, **kwargs):
        task_id = None
        task_state = None
        task_result = None
        task_ready = None

        if 'task_id' in request.data:

            task_id = request.data['task_id']
            task_result = AsyncResult(task_id)

            task_ready = task_result.ready()

            task_state = task_result.state
            task_result = task_result.result

        return Response({
            'task_id': task_id,
            'task_state': task_state,
            'task_result': task_result,
            'task_ready': task_ready
        })

    @action(detail=False, url_path=r'search-file')
    def search_file(self, request, pk=None):
        file_path = None
        count = None
        if 'file_path' in request.data:
            file_path = request.data['file_path']
            count = file_init.delay(file_path)
            print(count)
        return Response({'status': 'start', 'task_id': f'{count}'})

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

    def create(self, request, **kwargs):
        try:
            request_data = request.data
            print(request_data)
            serializer = self.get_serializer(data=request_data)
            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)
            self.get_success_headers(serializer.data)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            file = queryset.get(id=pk)
            serializer = self.get_serializer(file)

            return Response(serializer.data)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None, *args, **kwargs):

        try:
            queryset = self.get_queryset()
            file = queryset.get(id=pk)
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

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            file = queryset.get(id=pk)

            file.delete()
            return Response(status=status.HTTP_200_OK)

        except Exception:
            return Response({"errors": {
                "body": [
                    "Bad Request"
                ]
            }}, status=status.HTTP_404_NOT_FOUND)
