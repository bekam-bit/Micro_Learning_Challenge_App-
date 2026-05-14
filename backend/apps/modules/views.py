from rest_framework import generics, permissions
from django.db.models import BooleanField, Exists, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from config.api_cache import get_cached_response, invalidate_namespace, set_cached_response
from config.pagination import StandardPageNumberPagination

from apps.progress.models import UserProgress
from apps.users.permissions import IsAdminRole

from .models import Module, ModuleEnrollment
from .serializers import ModuleSerializer


def _with_user_learning_state(queryset, user):
	if not user.is_authenticated:
		return queryset.annotate(
			user_is_enrolled=Value(False, output_field=BooleanField()),
			user_progress_percent=Value(0, output_field=IntegerField()),
			user_completed_parts=Value(0, output_field=IntegerField()),
			user_total_parts=Value(0, output_field=IntegerField()),
		)

	enrollment_qs = ModuleEnrollment.objects.filter(user=user, module_id=OuterRef('pk'))
	progress_qs = UserProgress.objects.filter(user=user, module_id=OuterRef('pk'))

	return queryset.annotate(
		user_is_enrolled=Exists(enrollment_qs),
		user_progress_percent=Coalesce(
			Subquery(progress_qs.values('progress_percent')[:1]),
			Value(0),
			output_field=IntegerField(),
		),
		user_completed_parts=Coalesce(
			Subquery(progress_qs.values('completed_parts')[:1]),
			Value(0),
			output_field=IntegerField(),
		),
		user_total_parts=Coalesce(
			Subquery(progress_qs.values('total_parts')[:1]),
			Value(0),
			output_field=IntegerField(),
		),
	)


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

		queryset = _with_user_learning_state(queryset, user)

		return queryset.order_by(sort_by, 'id')

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def list(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='modules')
		if cached_response is not None:
			return cached_response

		response = super().list(request, *args, **kwargs)
		set_cached_response(request, namespace='modules', response=response)
		return response

	def create(self, request, *args, **kwargs):
		response = super().create(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('modules')
		return response


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
	queryset = Module.objects.select_related('category').all()
	serializer_class = ModuleSerializer

	def get_queryset(self):
		queryset = super().get_queryset()
		user = self.request.user
		if not (user.is_authenticated and getattr(user, 'role', None) == 'admin'):
			queryset = queryset.filter(category__is_active=True)

		return _with_user_learning_state(queryset, user)

	def get_permissions(self):
		if self.request.method in permissions.SAFE_METHODS:
			return [permissions.IsAuthenticated()]
		return [permissions.IsAuthenticated(), IsAdminRole()]

	def retrieve(self, request, *args, **kwargs):
		cached_response = get_cached_response(request, namespace='modules')
		if cached_response is not None:
			return cached_response

		response = super().retrieve(request, *args, **kwargs)
		set_cached_response(request, namespace='modules', response=response)
		return response

	def update(self, request, *args, **kwargs):
		response = super().update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('modules')
		return response

	def partial_update(self, request, *args, **kwargs):
		response = super().partial_update(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('modules')
		return response

	def destroy(self, request, *args, **kwargs):
		response = super().destroy(request, *args, **kwargs)
		if response.status_code < 400:
			invalidate_namespace('modules')
		return response


class ModuleEnrollView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request, pk):
		module = get_object_or_404(Module, pk=pk, category__is_active=True)
		enrollment, created = ModuleEnrollment.objects.get_or_create(
			user=request.user,
			module=module,
		)
		invalidate_namespace('modules')
		status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
		return Response(
			{
				'module_id': module.id,
				'enrolled': True,
				'enrolled_at': enrollment.enrolled_at,
				'created': created,
			},
			status=status_code,
		)
