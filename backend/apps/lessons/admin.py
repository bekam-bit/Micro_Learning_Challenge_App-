from django.contrib import admin
from .models import Lesson

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
	list_display = ('id', 'title', 'module', 'category')
	search_fields = ('title',)
	list_filter = ('module', 'category')
