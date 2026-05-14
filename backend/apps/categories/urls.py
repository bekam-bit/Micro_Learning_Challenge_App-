from django.urls import path

from .views import CategoryDetailView, CategoryListCreateView

urlpatterns = [
    path('', CategoryListCreateView.as_view(), name='category_list_create'),
    path('<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
]
