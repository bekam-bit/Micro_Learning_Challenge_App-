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
	list_filter = ('date', 'challenge__difficulty')
	search_fields = ('challenge__title', 'challenge__description')
	list_select_related = ('challenge', 'challenge__lesson', 'challenge__module', 'challenge__category')
