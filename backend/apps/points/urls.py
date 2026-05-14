from django.urls import path

from .views import AdminPointTransactionListView

urlpatterns = [
    path('admin/transactions/', AdminPointTransactionListView.as_view(), name='admin_points_transactions'),
]
