from rest_framework import generics, permissions

from config.pagination import StandardPageNumberPagination

from apps.users.permissions import IsAdminRole

from .models import Module
from .serializers import ModuleSerializer


class ModuleListCreateView(generics.ListCreateAPIView):
	queryset = Module.objects.select_related('category').all()
	serializer_class = ModuleSerializer
	pagination_class = StandardPageNumberPagination

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user
		if not (user.is_authenticated and getattr(user, 'role', None) == 'admin'):
			queryset = queryset.filter(category__is_active=True)

		category_id = self.request.query_params.get('category_id')
		if category_id:
			queryset = queryset.filter(category_id=category_id)

		search = self.request.query_params.get('search')
		if search:
			queryset = queryset.filter(title__icontains=search)

		sort_by = self.request.query_params.get('sort_by', 'title')
		allowed_sort_fields = {'title', '-title', 'created_at', '-created_at', 'updated_at', '-updated_at'}
		if sort_by not in allowed_sort_fields:
			sort_by = 'title'

		return queryset.order_by(sort_by, 'id')

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsAdminRole()]


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Module.objects.select_related('category').all()
	serializer_class = ModuleSerializer

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user
		if not (user.is_authenticated and getattr(user, 'role', None) == 'admin'):
			queryset = queryset.filter(category__is_active=True)
		return queryset

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsAdminRole()]
