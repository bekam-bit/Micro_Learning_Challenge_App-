from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    scope = "login"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }


class AdminActionRateThrottle(SimpleRateThrottle):
    scope = "admin_action"

    def get_cache_key(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {
            "scope": self.scope,
            "ident": str(user.pk),
        }


class NotificationActionRateThrottle(SimpleRateThrottle):
    scope = "notification_action"

    def get_cache_key(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return None
        return self.cache_format % {
            "scope": self.scope,
            "ident": str(user.pk),
        }


class PasswordResetRateThrottle(SimpleRateThrottle):
    scope = "password_reset"

    def get_cache_key(self, request, view):
        email = request.data.get("email") if hasattr(request, "data") else None
        ident = (email or self.get_ident(request) or "unknown").strip().lower()
        return self.cache_format % {
            "scope": self.scope,
            "ident": ident,
        }
