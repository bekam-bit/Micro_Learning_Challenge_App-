from rest_framework import generics, permissions

from config.pagination import StandardPageNumberPagination

from apps.users.permissions import IsAdminRole

from .models import Category
from .serializers import CategoryDetailSerializer, CategoryListSerializer, CategoryWriteSerializer
from django.db.models import Count


class CategoryListCreateView(generics.ListCreateAPIView):
	queryset = Category.objects.all().order_by('display_order', 'name')
	pagination_class = StandardPageNumberPagination

	def get_permissions(self):
		if self.request.method == 'POST':
			return [permissions.IsAuthenticated(), IsAdminRole()]
		return [permissions.AllowAny()]

	def get_serializer_class(self):
		if self.request.method == 'POST':
			return CategoryWriteSerializer
		return CategoryListSerializer

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user
		if user.is_authenticated and getattr(user, 'role', None) == 'admin':
			filtered_queryset = queryset
		else:
			filtered_queryset = queryset.filter(is_active=True)

		search = self.request.query_params.get('search')
		if search:
			filtered_queryset = filtered_queryset.filter(name__icontains=search)

		sort_by = self.request.query_params.get('sort_by', 'display_order')
		allowed_sort_fields = {'name', '-name', 'display_order', '-display_order', 'created_at', '-created_at'}
		if sort_by not in allowed_sort_fields:
			sort_by = 'display_order'

		# Annotate module_count efficiently
		return filtered_queryset.annotate(module_count=Count('modules')).order_by(sort_by, 'name')


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Category.objects.all()

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user
		if user.is_authenticated and getattr(user, 'role', None) == 'admin':
			return queryset
		return queryset.filter(is_active=True)

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def get_serializer_class(self):
		if self.request.method in ('PUT', 'PATCH'):
			return CategoryWriteSerializer
		return CategoryDetailSerializer
