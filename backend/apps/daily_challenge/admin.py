from django.contrib import admin
from .models import DailyChallenge


@admin.register(DailyChallenge)
class DailyChallengeAdmin(admin.ModelAdmin):
	list_display = (
		'id',
		'date',
		'title',
		'difficulty',
		'points',
		'time_limit_minutes',
		'lesson',
		'module',
		'category',
	)
	list_filter = ('date', 'difficulty')
	search_fields = ('title', 'description')
	list_select_related = ('lesson', 'module', 'category')
