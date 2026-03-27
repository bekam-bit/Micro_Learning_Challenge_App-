from django.urls import path

from .views import quiz_health

app_name = "quiz"

urlpatterns = [
    path("health/", quiz_health, name="health"),
]