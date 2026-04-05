from django.contrib import admin
from .models.Quiz import Quiz
from .models.Question import Question
from .models.Answer import Answer
from .models.QuizSubmission import QuizSubmission


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'lesson', 'created_at', 'updated_at']
    list_filter = ['lesson', 'created_at']
    search_fields = ['title']
    list_select_related = ['lesson']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'question_type', 'prompt', 'order', 'created_at']
    list_filter = ['quiz', 'question_type']
    search_fields = ['prompt']
    list_select_related = ['quiz']


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'text', 'is_correct', 'order', 'has_explanation']
    list_filter = ['question', 'is_correct']
    search_fields = ['text', 'explanation']
    list_select_related = ['question']

    @admin.display(description='Has Explanation', boolean=True)
    def has_explanation(self, obj):
        return bool(obj.explanation.strip())


@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'quiz', 'user', 'is_submitted', 'score', 'correct_answers', 'total_questions', 'submitted_at']
    list_filter = ['is_submitted', 'submitted_at']
    search_fields = ['quiz__title', 'user__username', 'user__email']
    list_select_related = ['quiz', 'user']