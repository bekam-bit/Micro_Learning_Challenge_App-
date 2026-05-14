from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPageNumberPagination

from .models import Notification
from .serializers import NotificationSerializer
from .services import cleanup_old_read_notifications
from apps.users.throttles import NotificationActionRateThrottle


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPageNumberPagination

    def _base_queryset(self):
        return Notification.objects.filter(user=self.request.user).only('id', 'message', 'is_read', 'created_at')

    def get_queryset(self):
        cleanup_old_read_notifications()
        queryset = self._base_queryset()

        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            value = is_read.strip().lower()
            if value in {'true', '1', 'yes'}:
                queryset = queryset.filter(is_read=True)
            elif value in {'false', '0', 'no'}:
                queryset = queryset.filter(is_read=False)

        return queryset.order_by('-created_at', '-id')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        response.data['unread_count'] = self._base_queryset().filter(is_read=False).count()
        return response


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationActionRateThrottle]

    def post(self, request, pk):
        notification = generics.get_object_or_404(Notification, pk=pk, user=request.user)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])
        cleanup_old_read_notifications()
        return Response({'detail': 'Notification marked as read.'}, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [NotificationActionRateThrottle]

    def post(self, request):
        updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        cleanup_old_read_notifications()
        return Response({'detail': 'All notifications marked as read.', 'updated_count': updated_count}, status=status.HTTP_200_OK)
