from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.db.models import Count, IntegerField, OuterRef, Subquery, Value
from django.db.models.functions import Coalesce

from .models import User, UserDailyActivity, UserProfile
from apps.progress.models import UserProgress
from apps.quiz.models import QuizSubmission


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	list_display = (
		"id",
		"username",
		"email",
		"role",
		"total_modules_completed",
		"total_lessons_completed",
		"total_quizzes_completed",
		"is_staff",
		"is_active",
		"date_joined",
	)
	list_filter = ("role", "is_staff", "is_active", "is_superuser")
	search_fields = ("username", "email")
	inlines = [UserProfileInline]

	fieldsets = DjangoUserAdmin.fieldsets + (
		("Application Role", {"fields": ("role",)}),
	)

	add_fieldsets = DjangoUserAdmin.add_fieldsets + (
		("Application Role", {"fields": ("role",)}),
	)

	def get_queryset(self, request):
		modules_completed_subquery = (
			UserProgress.objects.filter(
				user_id=OuterRef('pk'),
				module__isnull=False,
				completed=True,
			)
			.values('user_id')
			.annotate(total=Count('id'))
			.values('total')[:1]
		)
		lessons_completed_subquery = (
			UserProgress.objects.filter(
				user_id=OuterRef('pk'),
				lesson__isnull=False,
				completed=True,
			)
			.values('user_id')
			.annotate(total=Count('id'))
			.values('total')[:1]
		)
		quizzes_completed_subquery = (
			QuizSubmission.objects.filter(
				user_id=OuterRef('pk'),
				is_submitted=True,
			)
			.values('user_id')
			.annotate(total=Count('id'))
			.values('total')[:1]
		)

		return super().get_queryset(request).annotate(
			total_modules_completed_value=Coalesce(
				Subquery(modules_completed_subquery, output_field=IntegerField()),
				Value(0),
			),
			total_lessons_completed_value=Coalesce(
				Subquery(lessons_completed_subquery, output_field=IntegerField()),
				Value(0),
			),
			total_quizzes_completed_value=Coalesce(
				Subquery(quizzes_completed_subquery, output_field=IntegerField()),
				Value(0),
			),
		)

	@admin.display(description='Modules Completed', ordering='total_modules_completed_value')
	def total_modules_completed(self, obj):
		return obj.total_modules_completed_value

	@admin.display(description='Lessons Completed', ordering='total_lessons_completed_value')
	def total_lessons_completed(self, obj):
		return obj.total_lessons_completed_value

	@admin.display(description='Quizzes Completed', ordering='total_quizzes_completed_value')
	def total_quizzes_completed(self, obj):
		return obj.total_quizzes_completed_value


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"user",
		"total_points",
		"modules_completed_count",
		"lessons_completed_count",
		"challenges_completed_count",
		"current_streak",
		"max_streak",
		"last_activity_date",
	)
	search_fields = ("user__username", "user__email")
	list_select_related = ("user",)


@admin.register(UserDailyActivity)
class UserDailyActivityAdmin(admin.ModelAdmin):
	list_display = (
		"id",
		"user",
		"activity_date",
		"activity_score",
		"points_earned",
		"modules_completed",
		"lessons_completed",
		"challenges_completed",
	)
	list_filter = ("activity_date",)
	search_fields = ("user__username", "user__email")
	list_select_related = ("user",)
