from rest_framework import serializers
from .models import Lesson

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'video_url', 'video_file', 'order',
            'category', 'module', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        # Ensure at least one of video_url or video_file is provided
        video_url = data.get('video_url')
        video_file = data.get('video_file')
        if not video_url and not video_file:
            raise serializers.ValidationError("Either video_url or video_file must be provided.")
        return data
