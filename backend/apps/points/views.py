from rest_framework import filters, generics, permissions

from config.pagination import StandardPageNumberPagination

from apps.users.permissions import IsAdminRole

from .models import PointTransaction
from .serializers import PointTransactionAdminSerializer


class AdminPointTransactionListView(generics.ListAPIView):
    serializer_class = PointTransactionAdminSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]
    pagination_class = StandardPageNumberPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__username', 'user__email', 'reason', 'source_type']
    ordering_fields = ['id', 'points', 'created_at', 'updated_at', 'user__username']
    ordering = ['-created_at', '-id']

    def get_queryset(self):
        queryset = PointTransaction.objects.select_related('user').all()

        user_id = self.request.query_params.get('user_id')
        if user_id and user_id.isdigit():
            queryset = queryset.filter(user_id=int(user_id))

        source_type = self.request.query_params.get('source_type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)

        source_id = self.request.query_params.get('source_id')
        if source_id and source_id.isdigit():
            queryset = queryset.filter(source_id=int(source_id))

        return queryset.order_by('-created_at', '-id')
