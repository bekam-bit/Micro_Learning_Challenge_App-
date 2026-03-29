from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
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

User = get_user_model()


class RegisterView(generics.CreateAPIView):
	serializer_class = RegisterSerializer
	permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
	serializer_class = ProfileSerializer
	permission_classes = [permissions.IsAuthenticated]

	def get_object(self):
		return self.request.user


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
	queryset = User.objects.all().order_by("id")
	serializer_class = UserListSerializer
	permission_classes = [permissions.IsAuthenticated, IsAdminRole]
	throttle_classes = [AdminActionRateThrottle]


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
