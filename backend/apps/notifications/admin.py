from django.contrib import admin
from .models import Notification, NotificationRetentionSetting


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'is_read', 'created_at')
	list_filter = ('is_read', 'created_at')
	search_fields = ('user__username', 'user__email', 'message')
	list_select_related = ('user',)


@admin.register(NotificationRetentionSetting)
class NotificationRetentionSettingAdmin(admin.ModelAdmin):
	list_display = ('enabled', 'retention_days', 'updated_at')
	readonly_fields = ('singleton_key', 'updated_at')

	def has_add_permission(self, request):
		if NotificationRetentionSetting.objects.exists():
			return False
		return super().has_add_permission(request)

	def has_delete_permission(self, request, obj=None):
		return False
