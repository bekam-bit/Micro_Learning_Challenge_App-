from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import UserDailyActivity, UserProfile

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    total_points_earned = serializers.IntegerField(source="total_points", read_only=True)
    modules_completion_percentage = serializers.FloatField(read_only=True)
    lessons_completion_percentage = serializers.FloatField(read_only=True)
    challenges_completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "profile_picture",
            "total_points",
            "total_points_earned",
            "modules_completed_count",
            "modules_total_count",
            "modules_completion_percentage",
            "lessons_completed_count",
            "lessons_total_count",
            "lessons_completion_percentage",
            "challenges_completed_count",
            "challenges_total_count",
            "challenges_completion_percentage",
            "current_streak",
            "max_streak",
            "last_activity_date",
        ]

    def validate(self, attrs):
        checks = [
            ("modules_completed_count", "modules_total_count"),
            ("lessons_completed_count", "lessons_total_count"),
            ("challenges_completed_count", "challenges_total_count"),
        ]

        for completed_field, total_field in checks:
            completed = attrs.get(completed_field)
            total = attrs.get(total_field)
            if completed is not None and total is not None and completed > total:
                raise serializers.ValidationError(
                    {completed_field: f"{completed_field} cannot be greater than {total_field}"}
                )

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "date_joined"]
        read_only_fields = ["id", "date_joined", "role"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        UserProfile.objects.get_or_create(user=user)
        return user


class ProfileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)
    knowledge_momentum = serializers.SerializerMethodField(read_only=True)
    total_modules_completed = serializers.IntegerField(read_only=True)
    total_lessons_completed = serializers.IntegerField(read_only=True)
    total_quizzes_completed = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "date_joined",
            "profile",
            "knowledge_momentum",
            "total_modules_completed",
            "total_lessons_completed",
            "total_quizzes_completed",
        ]
        read_only_fields = ["id", "role", "date_joined"]

    def get_knowledge_momentum(self, instance):
        request = self.context.get("request")
        year = date.today().year
        if request is not None:
            year_value = request.query_params.get("year")
            if year_value and year_value.isdigit():
                year = int(year_value)

        start_date = date(year, 1, 1)
        end_date = min(date.today(), date(year, 12, 31))

        activity_rows = UserDailyActivity.objects.filter(
            user=instance,
            activity_date__range=(start_date, end_date),
        ).values("activity_date", "activity_score")

        activity_map = {
            row["activity_date"]: row["activity_score"]
            for row in activity_rows
        }

        days = []
        current = start_date
        while current <= end_date:
            score = activity_map.get(current, 0)
            days.append(
                {
                    "date": current.isoformat(),
                    "score": score,
                    "level": UserDailyActivity.score_to_level(score),
                }
            )
            current += timedelta(days=1)

        active_days = sum(1 for item in days if item["score"] > 0)
        total_score = sum(item["score"] for item in days)

        return {
            "year": year,
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "active_days": active_days,
            "total_score": total_score,
            "days": days,
        }

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        request = self.context.get("request")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if request is not None:
            uploaded_picture = request.FILES.get("profile_picture")
            uploaded_bio = request.data.get("bio")

            if uploaded_picture is not None or uploaded_bio is not None:
                profile_data = profile_data or {}
                if uploaded_picture is not None:
                    profile_data["profile_picture"] = uploaded_picture
                if uploaded_bio is not None:
                    profile_data["bio"] = uploaded_bio

        if profile_data is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["username"] = user.username
        token["email"] = user.email
        token["role"] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "role": self.user.role,
        }
        return data


class UserListSerializer(serializers.ModelSerializer):
    total_modules_completed = serializers.IntegerField(read_only=True)
    total_lessons_completed = serializers.IntegerField(read_only=True)
    total_quizzes_completed = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "date_joined",
            "total_modules_completed",
            "total_lessons_completed",
            "total_quizzes_completed",
        ]
        read_only_fields = fields


class UserRoleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["role"]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs["refresh"]
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError as exc:
            raise serializers.ValidationError({"refresh": "Invalid or expired token"}) from exc
