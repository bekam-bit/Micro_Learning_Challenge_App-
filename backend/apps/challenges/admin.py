from django.contrib import admin
from .models import Challenge, ChallengeAttempt, ChallengeAttemptAnswer, ChallengeQuestion, ChallengeSubmission
from .forms import ChallengeQuestionAdminForm


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
	list_display = ('title', 'difficulty', 'points', 'lesson', 'module', 'category')
	search_fields = ('title', 'description')
	list_filter = ('difficulty',)


@admin.register(ChallengeSubmission)
class ChallengeSubmissionAdmin(admin.ModelAdmin):
	list_display = ('id', 'challenge', 'user', 'status', 'score', 'submitted_at')
	search_fields = ('challenge__title', 'user__username', 'response_text')
	list_filter = ('status', 'submitted_at')


@admin.register(ChallengeQuestion)
class ChallengeQuestionAdmin(admin.ModelAdmin):
	form = ChallengeQuestionAdminForm
	list_display = ('id', 'challenge', 'question_type', 'order', 'max_score')
	search_fields = ('challenge__title', 'question_text')
	list_filter = ('challenge', 'question_type')

	class Media:
		js = ('admin/challenge_question_form.js',)


@admin.register(ChallengeAttempt)
class ChallengeAttemptAdmin(admin.ModelAdmin):
	list_display = ('id', 'challenge', 'user', 'is_submitted', 'points_awarded', 'deadline_at', 'submitted_at')
	search_fields = ('challenge__title', 'user__username')
	list_filter = ('is_submitted', 'is_within_time_limit')


@admin.register(ChallengeAttemptAnswer)
class ChallengeAttemptAnswerAdmin(admin.ModelAdmin):
	list_display = ('id', 'attempt', 'question', 'is_correct', 'score')
	search_fields = ('attempt__challenge__title', 'attempt__user__username', 'question__question_text')
	list_filter = ('is_correct',)
