from rest_framework import serializers

from .models import UserProgress


class UserProgressSerializer(serializers.ModelSerializer):
    owner_type = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()
    owner_title = serializers.SerializerMethodField()

    class Meta:
        model = UserProgress
        fields = [
            "id",
            "owner_type",
            "owner_id",
            "owner_title",
            "completed",
            "points_earned",
            "completed_parts",
            "total_parts",
            "progress_percent",
            "created_at",
            "updated_at",
            "challenge",
            "lesson",
            "module",
        ]
        read_only_fields = fields

    def get_owner_type(self, obj):
        if obj.challenge_id:
            return "challenge"
        if obj.lesson_id:
            return "lesson"
        return "module"

    def get_owner_id(self, obj):
        if obj.challenge_id:
            return obj.challenge_id
        if obj.lesson_id:
            return obj.lesson_id
        return obj.module_id

    def get_owner_title(self, obj):
        if obj.challenge_id:
            return obj.challenge.title
        if obj.lesson_id:
            return obj.lesson.title
        return obj.module.title


class AdminUserProgressSerializer(UserProgressSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta(UserProgressSerializer.Meta):
        fields = [
            "user_id",
            "username",
            "email",
            *UserProgressSerializer.Meta.fields,
        ]
