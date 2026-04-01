
from rest_framework import generics, permissions
from apps.users.permissions import IsAdminRole
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
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

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
			return [permissions.AllowAny()]
		return [permissions.IsAuthenticated(), IsAdminRole()]
