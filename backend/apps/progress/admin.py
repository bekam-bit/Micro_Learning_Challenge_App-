from django.contrib import admin
from .models import UserProgress


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'user',
		'owner_type',
		'owner_title',
		'completed',
		'progress_percent',
		'completed_parts',
		'total_parts',
		'points_earned',
		'updated_at',
	)
	list_filter = ('completed', 'updated_at', 'created_at')
	search_fields = (
		'user__username',
		'user__email',
		'challenge__title',
		'lesson__title',
		'module__title',
	)
	readonly_fields = ('created_at', 'updated_at')
	list_select_related = ('user', 'challenge', 'lesson', 'module')

	def get_queryset(self, request):
		return super().get_queryset(request).select_related('user', 'challenge', 'lesson', 'module')

	@admin.display(description='Owner Type')
	def owner_type(self, obj):
		if obj.challenge_id:
			return 'challenge'
		if obj.lesson_id:
			return 'lesson'
		return 'module'

	@admin.display(description='Owner Title')
	def owner_title(self, obj):
		if obj.challenge_id:
			return obj.challenge.title
		if obj.lesson_id:
			return obj.lesson.title
		return obj.module.title
