from django.urls import path

from .views import ModuleDetailView, ModuleEnrollView, ModuleListCreateView

urlpatterns = [
	path('', ModuleListCreateView.as_view(), name='module_list_create'),
	path('<int:pk>/enroll/', ModuleEnrollView.as_view(), name='module_enroll'),
	path('<int:pk>/', ModuleDetailView.as_view(), name='module_detail'),
]
