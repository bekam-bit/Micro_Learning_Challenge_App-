from django.contrib import admin
from .models import Module, ModuleEnrollment


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('title',)


@admin.register(ModuleEnrollment)
class ModuleEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'module', 'enrolled_at')
    list_filter = ('module',)
    search_fields = ('user__username', 'user__email', 'module__title')
