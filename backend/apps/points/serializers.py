from rest_framework import serializers

from .models import PointTransaction


class PointTransactionAdminSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PointTransaction
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'points',
            'source_type',
            'source_id',
            'reason',
            'metadata',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
