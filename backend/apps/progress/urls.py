from django.urls import path

from .views import (
    AdminUserProgressListView,
    AdminUserProgressSummaryView,
    UserProgressListView,
    UserProgressSummaryView,
)

urlpatterns = [
    path('', UserProgressListView.as_view(), name='user_progress_list'),
    path('summary/', UserProgressSummaryView.as_view(), name='user_progress_summary'),
    path('admin/', AdminUserProgressListView.as_view(), name='admin_user_progress_list'),
    path('admin/summary/', AdminUserProgressSummaryView.as_view(), name='admin_user_progress_summary'),
]
