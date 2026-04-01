from django.urls import path

from .views import ModuleDetailView, ModuleListCreateView

urlpatterns = [
	path('', ModuleListCreateView.as_view(), name='module_list_create'),
	path('<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
]
