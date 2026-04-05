import logging
from time import perf_counter
from datetime import datetime, time

from django.conf import settings
from django.db import connection
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPageNumberPagination
from config.api_cache import get_cached_response, set_cached_response

from .models import UserProgress
from .serializers import AdminUserProgressSerializer, UserProgressSerializer
from apps.users.permissions import IsAdminRole


logger = logging.getLogger(__name__)


def _parse_datetime_bound(value: str, *, is_end: bool):
	parsed_dt = parse_datetime(value)
	if parsed_dt is not None:
		if timezone.is_naive(parsed_dt):
			return timezone.make_aware(parsed_dt, timezone.get_current_timezone())
		return parsed_dt

	parsed_date = parse_date(value)
	if parsed_date is None:
		raise ValidationError({'detail': 'Invalid date format. Use ISO datetime or YYYY-MM-DD.'})

	bound_time = time.max if is_end else time.min
	dt = datetime.combine(parsed_date, bound_time)
	return timezone.make_aware(dt, timezone.get_current_timezone())


def _apply_updated_at_range(queryset, query_params):
	from_value = query_params.get('from')
	to_value = query_params.get('to')

	if from_value:
		from_dt = _parse_datetime_bound(from_value, is_end=False)
		queryset = queryset.filter(updated_at__gte=from_dt)

	if to_value:
		to_dt = _parse_datetime_bound(to_value, is_end=True)
		queryset = queryset.filter(updated_at__lte=to_dt)

	return queryset


def _build_progress_summary(queryset):
	aggregate_data = queryset.aggregate(
		challenges_total=Count('id', filter=Q(challenge__isnull=False)),
		challenges_completed=Count('id', filter=Q(challenge__isnull=False, completed=True)),
		lessons_total=Count('id', filter=Q(lesson__isnull=False)),
		lessons_completed=Count('id', filter=Q(lesson__isnull=False, completed=True)),
		modules_total=Count('id', filter=Q(module__isnull=False)),
		modules_completed=Count('id', filter=Q(module__isnull=False, completed=True)),
		challenge_points_earned=Sum('points_earned', filter=Q(challenge__isnull=False)),
	)

	def summarize(total, completed):
		total = int(total or 0)
		completed = int(completed or 0)
		percentage = round((completed / total) * 100, 2) if total else 0.0
		return {
			'completed': completed,
			'total': total,
			'percentage': percentage,
		}

	return {
		'challenges': summarize(aggregate_data['challenges_total'], aggregate_data['challenges_completed']),
		'lessons': summarize(aggregate_data['lessons_total'], aggregate_data['lessons_completed']),
		'modules': summarize(aggregate_data['modules_total'], aggregate_data['modules_completed']),
		'points_earned': int(aggregate_data['challenge_points_earned'] or 0),
	}


def _run_with_query_profile(endpoint_name: str, callback):
	if not getattr(settings, 'API_QUERY_PROFILE_ENABLED', False):
		return callback()

	threshold_queries = int(getattr(settings, 'API_QUERY_PROFILE_QUERY_THRESHOLD', 15))
	threshold_ms = float(getattr(settings, 'API_QUERY_PROFILE_MS_THRESHOLD', 120))

	force_debug_before = connection.force_debug_cursor
	if not force_debug_before:
		connection.force_debug_cursor = True

	queries_before = len(connection.queries)
	start = perf_counter()
	try:
		result = callback()
	finally:
		elapsed_ms = (perf_counter() - start) * 1000
		query_count = max(0, len(connection.queries) - queries_before)
		if (query_count >= threshold_queries) or (elapsed_ms >= threshold_ms):
			logger.warning(
				'API query profile threshold exceeded for %s: queries=%s elapsed_ms=%.2f',
				endpoint_name,
				query_count,
				elapsed_ms,
			)
		if not force_debug_before:
			connection.force_debug_cursor = False

	return result


def _summary_cache_enabled():
	return bool(getattr(settings, 'SUMMARY_ENDPOINT_CACHE_ENABLED', False))


def _summary_cache_ttl():
	return int(getattr(settings, 'SUMMARY_ENDPOINT_CACHE_TTL_SECONDS', 60))


class UserProgressListView(generics.ListAPIView):
	serializer_class = UserProgressSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_queryset(self):
		queryset = UserProgress.objects.filter(user=self.request.user)

		owner_type = self.request.query_params.get('owner_type')
		if owner_type == 'challenge':
			queryset = queryset.filter(challenge__isnull=False)
		elif owner_type == 'lesson':
			queryset = queryset.filter(lesson__isnull=False)
		elif owner_type == 'module':
			queryset = queryset.filter(module__isnull=False)

		completed = self.request.query_params.get('completed')
		if completed is not None:
			completed_bool = completed.lower() in {'1', 'true', 'yes'}
			queryset = queryset.filter(completed=completed_bool)

		return queryset.select_related('challenge', 'lesson', 'module').order_by('id')


class UserProgressSummaryView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def get(self, request):
		cache_identity = f'user:{request.user.pk}'
		if _summary_cache_enabled():
			cached = get_cached_response(
				request,
				'progress_user_summary',
				allow_authenticated=True,
				identity=cache_identity,
			)
			if cached is not None:
				return cached

		queryset = UserProgress.objects.filter(user=request.user)
		payload = _run_with_query_profile('user_progress_summary', lambda: _build_progress_summary(queryset))
		response = Response(payload)
		if _summary_cache_enabled():
			set_cached_response(
				request,
				'progress_user_summary',
				response,
				timeout=_summary_cache_ttl(),
				allow_authenticated=True,
				identity=cache_identity,
			)
		return response


class AdminUserProgressListView(generics.ListAPIView):
	serializer_class = AdminUserProgressSerializer
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]
	pagination_class = StandardPageNumberPagination
	filter_backends = [filters.SearchFilter, filters.OrderingFilter]
	search_fields = [
		'user__username',
		'user__email',
		'challenge__title',
		'lesson__title',
		'module__title',
	]
	ordering_fields = [
		'id',
		'updated_at',
		'created_at',
		'points_earned',
		'progress_percent',
		'completed_parts',
		'total_parts',
		'user__username',
	]
	ordering = ['-updated_at', '-id']

	def get_queryset(self):
		queryset = UserProgress.objects.all()
		queryset = _apply_updated_at_range(queryset, self.request.query_params)

		user_id = self.request.query_params.get('user_id')
		if user_id and user_id.isdigit():
			queryset = queryset.filter(user_id=int(user_id))

		owner_type = self.request.query_params.get('owner_type')
		if owner_type == 'challenge':
			queryset = queryset.filter(challenge__isnull=False)
		elif owner_type == 'lesson':
			queryset = queryset.filter(lesson__isnull=False)
		elif owner_type == 'module':
			queryset = queryset.filter(module__isnull=False)

		completed = self.request.query_params.get('completed')
		if completed is not None:
			completed_bool = completed.lower() in {'1', 'true', 'yes'}
			queryset = queryset.filter(completed=completed_bool)

		return queryset.select_related('user', 'challenge', 'lesson', 'module').only(
			'id',
			'user_id',
			'challenge_id',
			'lesson_id',
			'module_id',
			'completed',
			'points_earned',
			'completed_parts',
			'total_parts',
			'progress_percent',
			'created_at',
			'updated_at',
			'user__id',
			'user__username',
			'user__email',
			'challenge__id',
			'challenge__title',
			'lesson__id',
			'lesson__title',
			'module__id',
			'module__title',
		).order_by('id')


class AdminUserProgressSummaryView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]

	def get(self, request):
		cache_identity = f'admin:{request.user.pk}'
		if _summary_cache_enabled():
			cached = get_cached_response(
				request,
				'progress_admin_summary',
				allow_authenticated=True,
				identity=cache_identity,
			)
			if cached is not None:
				return cached

		queryset = UserProgress.objects.all()
		queryset = _apply_updated_at_range(queryset, request.query_params)

		user_id = request.query_params.get('user_id')
		if user_id and user_id.isdigit():
			queryset = queryset.filter(user_id=int(user_id))

		owner_type = request.query_params.get('owner_type')
		if owner_type == 'challenge':
			queryset = queryset.filter(challenge__isnull=False)
		elif owner_type == 'lesson':
			queryset = queryset.filter(lesson__isnull=False)
		elif owner_type == 'module':
			queryset = queryset.filter(module__isnull=False)

		payload = _run_with_query_profile('admin_user_progress_summary', lambda: _build_progress_summary(queryset))
		payload['users_tracked'] = queryset.values('user_id').distinct().count()
		response = Response(payload)
		if _summary_cache_enabled():
			set_cached_response(
				request,
				'progress_admin_summary',
				response,
				timeout=_summary_cache_ttl(),
				allow_authenticated=True,
				identity=cache_identity,
			)
		return response
