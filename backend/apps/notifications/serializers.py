from django.utils import timezone
from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    day_bucket = serializers.SerializerMethodField()
    day_tag = serializers.SerializerMethodField()
    day_date = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'day_bucket', 'day_tag', 'day_date']
        read_only_fields = ['id', 'message', 'created_at', 'day_bucket', 'day_tag', 'day_date']

    def _get_today_localdate(self):
        today = self.context.get('_today_localdate')
        if today is None:
            today = timezone.localdate()
            self.context['_today_localdate'] = today
        return today

    def _resolve_temporal_values(self, obj):
        cached = getattr(obj, '_notif_temporal_values', None)
        if cached is not None:
            return cached

        local_dt = timezone.localtime(obj.created_at)
        delta = (self._get_today_localdate() - local_dt.date()).days
        cached = (local_dt, delta)
        setattr(obj, '_notif_temporal_values', cached)
        return cached

    def get_day_bucket(self, obj):
        _, delta = self._resolve_temporal_values(obj)
        if delta == 0:
            return 'today'
        if delta == 1:
            return 'yesterday'
        return 'earlier'

    def get_day_tag(self, obj):
        local_dt, delta = self._resolve_temporal_values(obj)
        if delta == 0:
            return 'Today'
        if delta == 1:
            return 'Yesterday'
        return local_dt.strftime('%Y-%m-%d')

    def get_day_date(self, obj):
        local_dt, _ = self._resolve_temporal_values(obj)
        return local_dt.date().isoformat()
