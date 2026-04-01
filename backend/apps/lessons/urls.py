from django.urls import path
from .views import LessonListCreateView, LessonDetailView

urlpatterns = [
    path('', LessonListCreateView.as_view(), name='lesson_list_create'),
    path('<int:pk>/', LessonDetailView.as_view(), name='lesson_detail'),
]
