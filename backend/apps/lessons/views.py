
from rest_framework import generics, permissions
from apps.users.permissions import IsAdminRole
from config.api_cache import get_cached_response, invalidate_namespace, set_cached_response
from .models import Lesson
from .serializers import LessonSerializer

from config.pagination import StandardPageNumberPagination

class LessonListCreateView(generics.ListCreateAPIView):
	serializer_class = LessonSerializer
	pagination_class = StandardPageNumberPagination
    
	def get_queryset(self):
		module_id = self.request.query_params.get('module_id')
		queryset = Lesson.objects.all()
		if module_id:
			queryset = queryset.filter(module_id=module_id)
		return queryset.order_by('title')

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def list(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='lessons')
		if cached_response is not None:
			return cached_response

		response = super().list(request, *args, **kwargs)
		set_cached_response(request, namespace='lessons', response=response)
		return response

	def create(self, request, *args, **kwargs):
		response = super().create(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('lessons')
		return response

class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
	serializer_class = LessonSerializer

	def get_queryset(self):
		queryset = Lesson.objects.all()
		user = self.request.user
		# Only allow access to lessons in active modules for non-admins
		if not (user.is_authenticated and getattr(user, 'role', None) == 'admin'):
			queryset = queryset.filter(module__status='active')
		return queryset

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def retrieve(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='lessons')
		if cached_response is not None:
			return cached_response

		response = super().retrieve(request, *args, **kwargs)
		set_cached_response(request, namespace='lessons', response=response)
		return response

	def update(self, request, *args, **kwargs):
		response = super().update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('lessons')
		return response

	def partial_update(self, request, *args, **kwargs):
		response = super().partial_update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('lessons')
		return response

	def destroy(self, request, *args, **kwargs):
		response = super().destroy(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('lessons')
		return response
