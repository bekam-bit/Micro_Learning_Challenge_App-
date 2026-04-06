"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.urls import include, path


# def api_root(_request):
#     return JsonResponse({'message': 'Micro Learning Challenge API is running'})

urlpatterns = [
    # path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/categories/', include('apps.categories.urls')),
    path('api/modules/', include('apps.modules.urls')),
    path('api/lessons/', include('apps.lessons.urls')),
    path('api/challenges/', include('apps.challenges.urls')),
    path('api/daily-challenges/', include('apps.daily_challenge.urls')),
    path('api/progress/', include('apps.progress.urls')),
    path('api/points/', include('apps.points.urls')),
    path('api/quiz/', include('apps.quiz.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
