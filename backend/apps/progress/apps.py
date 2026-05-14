from django.apps import AppConfig


class ProgressConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.progress'

    def ready(self):
        # Import signals when the app registry is fully ready.
        from . import signals  # noqa: F401
