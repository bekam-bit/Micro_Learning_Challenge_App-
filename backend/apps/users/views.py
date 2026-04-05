from django.contrib.auth import get_user_model
from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .permissions import IsAdminRole
from .serializers import (
	LoginSerializer,
	LogoutSerializer,
	ProfileSerializer,
	RegisterSerializer,
	UserListSerializer,
	UserRoleUpdateSerializer,
)
from .throttles import AdminActionRateThrottle, LoginRateThrottle
from apps.progress.models import UserProgress
from apps.quiz.models import QuizSubmission

User = get_user_model()


def _with_completion_totals(queryset):
	modules_completed_subquery = (
		UserProgress.objects.filter(
			user_id=OuterRef('pk'),
			module__isnull=False,
			completed=True,
		)
		.values('user_id')
		.annotate(total=Count('id'))
		.values('total')[:1]
	)
	lessons_completed_subquery = (
		UserProgress.objects.filter(
			user_id=OuterRef('pk'),
			lesson__isnull=False,
			completed=True,
		)
		.values('user_id')
		.annotate(total=Count('id'))
		.values('total')[:1]
	)
	quizzes_completed_subquery = (
		QuizSubmission.objects.filter(
			user_id=OuterRef('pk'),
			is_submitted=True,
		)
		.values('user_id')
		.annotate(total=Count('id'))
		.values('total')[:1]
	)

	return queryset.annotate(
		total_modules_completed=Coalesce(
			Subquery(modules_completed_subquery, output_field=IntegerField()),
			Value(0),
		),
		total_lessons_completed=Coalesce(
			Subquery(lessons_completed_subquery, output_field=IntegerField()),
			Value(0),
		),
		total_quizzes_completed=Coalesce(
			Subquery(quizzes_completed_subquery, output_field=IntegerField()),
			Value(0),
		),
	)


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
	serializer_class = ProfileSerializer
	permission_classes = [permissions.IsAuthenticated]
	parser_classes = [JSONParser, MultiPartParser, FormParser]

	def get_object(self):
		queryset = _with_completion_totals(User.objects.select_related('profile'))
		return queryset.get(pk=self.request.user.pk)


class LoginView(TokenObtainPairView):
	serializer_class = LoginSerializer
	throttle_classes = [LoginRateThrottle]


class LogoutView(APIView):
	permission_classes = [permissions.IsAuthenticated]

	def post(self, request):
		serializer = LogoutSerializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response({"detail": "Successfully logged out"}, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
	queryset = _with_completion_totals(
		User.objects.only('id', 'username', 'email', 'role', 'is_active', 'date_joined').order_by("id")
	)
	serializer_class = UserListSerializer
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]
	throttle_classes = [AdminActionRateThrottle]


class UserDetailView(generics.RetrieveAPIView):
	serializer_class = UserListSerializer
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]
	throttle_classes = [AdminActionRateThrottle]

	def get_queryset(self):
		return _with_completion_totals(
			User.objects.only('id', 'username', 'email', 'role', 'is_active', 'date_joined')
		)


class UserRoleUpdateView(generics.UpdateAPIView):
	queryset = User.objects.all()
	serializer_class = UserRoleUpdateSerializer
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]
	http_method_names = ["patch"]
	throttle_classes = [AdminActionRateThrottle]

	def perform_update(self, serializer):
		target_user = self.get_object()
		new_role = serializer.validated_data.get("role", target_user.role)

		if target_user.role == User.ROLE_ADMIN and new_role != User.ROLE_ADMIN:
			admin_count = User.objects.filter(role=User.ROLE_ADMIN, is_active=True).count()
			if admin_count <= 1:
				raise ValidationError({"role": "Cannot demote the last active admin user"})

		serializer.save()
