from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, UserDailyActivity, UserProfile


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	can_delete = False
	extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
	list_display = ("id", "username", "email", "role", "is_staff", "is_active", "date_joined")
	list_filter = ("role", "is_staff", "is_active", "is_superuser")
	search_fields = ("username", "email")
	inlines = [UserProfileInline]

	fieldsets = DjangoUserAdmin.fieldsets + (
		("Application Role", {"fields": ("role",)}),
	)

	add_fieldsets = DjangoUserAdmin.add_fieldsets + (
		("Application Role", {"fields": ("role",)}),
	)


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
