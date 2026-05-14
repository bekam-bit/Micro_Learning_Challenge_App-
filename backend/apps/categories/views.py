from rest_framework import generics, permissions
from rest_framework.response import Response

from config.pagination import StandardPageNumberPagination
from config.api_cache import get_cached_response, invalidate_namespace, set_cached_response

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
		return [permissions.IsAuthenticated()]

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

	def list(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='categories')
		if cached_response is not None:
			return cached_response

		response = super().list(request, *args, **kwargs)
		set_cached_response(request, namespace='categories', response=response)
		return response

	def create(self, request, *args, **kwargs):
		response = super().create(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('categories')
		return response


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Category.objects.all()

	def get_queryset(self):
		queryset = super().get_queryset().prefetch_related('modules')
		user = self.request.user
		if user.is_authenticated and getattr(user, 'role', None) == 'admin':
			return queryset
		return queryset.filter(is_active=True)

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def get_serializer_class(self):
		if self.request.method in ('PUT', 'PATCH'):
			return CategoryWriteSerializer
		return CategoryDetailSerializer

	def retrieve(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='categories')
		if cached_response is not None:
			return cached_response

		response = super().retrieve(request, *args, **kwargs)
		set_cached_response(request, namespace='categories', response=response)
		return response

	def update(self, request, *args, **kwargs):
		response = super().update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('categories')
		return response

	def partial_update(self, request, *args, **kwargs):
		response = super().partial_update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('categories')
		return response

	def destroy(self, request, *args, **kwargs):
		response = super().destroy(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('categories')
		return response
