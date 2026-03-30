from django.contrib import admin
from .models.Quiz import Quiz
from .models.Question import Question
from .models.Answer import Answer


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'created_at', 'updated_at']
    search_fields = ['title']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'prompt', 'order', 'created_at']
    list_filter = ['quiz']
    search_fields = ['prompt']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'is_correct', 'order']
    list_filter = ['question', 'is_correct']
    search_fields = ['text']