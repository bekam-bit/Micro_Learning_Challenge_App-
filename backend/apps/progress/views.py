from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from rest_framework import filters, generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from config.pagination import StandardPageNumberPagination

from .models import UserProgress
from .serializers import AdminUserProgressSerializer, UserProgressSerializer
from apps.users.permissions import IsAdminRole


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
		queryset = UserProgress.objects.filter(user=request.user)

		challenge_qs = queryset.filter(challenge__isnull=False)
		lesson_qs = queryset.filter(lesson__isnull=False)
		module_qs = queryset.filter(module__isnull=False)

		def summarize(items):
			total = items.count()
			completed_count = items.filter(completed=True).count()
			if total == 0:
				percentage = 0.0
			else:
				percentage = round((completed_count / total) * 100, 2)
			return {
				'completed': completed_count,
				'total': total,
				'percentage': percentage,
			}

		payload = {
			'challenges': summarize(challenge_qs),
			'lessons': summarize(lesson_qs),
			'modules': summarize(module_qs),
			'points_earned': sum(challenge_qs.values_list('points_earned', flat=True)),
		}
		return Response(payload)


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

		return queryset.select_related('user', 'challenge', 'lesson', 'module').order_by('id')


class AdminUserProgressSummaryView(APIView):
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]

	def get(self, request):
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

		challenge_qs = queryset.filter(challenge__isnull=False)
		lesson_qs = queryset.filter(lesson__isnull=False)
		module_qs = queryset.filter(module__isnull=False)

		def summarize(items):
			total = items.count()
			completed_count = items.filter(completed=True).count()
			if total == 0:
				percentage = 0.0
			else:
				percentage = round((completed_count / total) * 100, 2)
			return {
				'completed': completed_count,
				'total': total,
				'percentage': percentage,
			}

		payload = {
			'users_tracked': queryset.values('user_id').distinct().count(),
			'challenges': summarize(challenge_qs),
			'lessons': summarize(lesson_qs),
			'modules': summarize(module_qs),
			'points_earned': sum(challenge_qs.values_list('points_earned', flat=True)),
		}
		return Response(payload)
