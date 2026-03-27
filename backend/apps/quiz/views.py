from django.http import JsonResponse


def quiz_health(request):
	return JsonResponse({"app": "quiz", "status": "ok"})
