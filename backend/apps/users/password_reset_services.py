import json
import logging
from urllib import error, request

import resend
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import linebreaksbr
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

logger = logging.getLogger(__name__)


def send_password_reset_email(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_link = _build_reset_link(uid=uid, token=token)

    subject = "Reset your password"
    text_body = (
        "We received a request to reset your password. "
        f"Use this link to continue: {reset_link}\n\n"
        "If you did not request a password reset, you can safely ignore this email."
    )
    html_body = (
        "<p>We received a request to reset your password.</p>"
        f"<p><a href=\"{reset_link}\">Reset password</a></p>"
        "<p>If you did not request this, you can safely ignore this email.</p>"
    )

    _send_transactional_email(
        to_email=user.email,
        subject=subject,
        text_body=text_body,
        html_body=html_body,
    )


def _build_reset_link(*, uid, token):
    frontend_base = getattr(settings, "PASSWORD_RESET_FRONTEND_URL", "")
    if frontend_base:
        separator = "&" if "?" in frontend_base else "?"
        return f"{frontend_base}{separator}uid={uid}&token={token}"

    backend_path = getattr(settings, "PASSWORD_RESET_CONFIRM_PATH", "/api/auth/password/reset/confirm/")
    base_url = getattr(settings, "BACKEND_BASE_URL", "").rstrip("/")
    if base_url:
        return f"{base_url}{backend_path}?uid={uid}&token={token}"
    return f"{backend_path}?uid={uid}&token={token}"


def _send_transactional_email(*, to_email, subject, text_body, html_body):
    provider = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()

    if provider == "resend":
        _send_with_resend(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)
        return
    if provider == "sendgrid":
        _send_with_sendgrid(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)
        return

    _send_with_smtp(to_email=to_email, subject=subject, text_body=text_body, html_body=html_body)


def _send_with_resend(*, to_email, subject, text_body, html_body):
    api_key = getattr(settings, "RESEND_API_KEY", "")
    if not api_key:
        raise ValueError("RESEND_API_KEY is required when EMAIL_PROVIDER=resend")

    resend.api_key = api_key
    resend.Emails.send(
        {
            "from": settings.DEFAULT_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "text": text_body,
            "html": html_body,
        }
    )


def _send_with_sendgrid(*, to_email, subject, text_body, html_body):
    api_key = getattr(settings, "SENDGRID_API_KEY", "")
    if not api_key:
        raise ValueError("SENDGRID_API_KEY is required when EMAIL_PROVIDER=sendgrid")

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": settings.DEFAULT_FROM_EMAIL},
        "subject": subject,
        "content": [
            {"type": "text/plain", "value": text_body},
            {"type": "text/html", "value": html_body},
        ],
    }
    _post_json(
        url="https://api.sendgrid.com/v3/mail/send",
        payload=payload,
        headers={"Authorization": f"Bearer {api_key}"},
    )


def _send_with_smtp(*, to_email, subject, text_body, html_body):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    message.attach_alternative(html_body or linebreaksbr(text_body), "text/html")
    message.send(fail_silently=False)


def _post_json(*, url, payload, headers):
    request_headers = {
        "Content-Type": "application/json",
        **headers,
    }
    body = json.dumps(payload).encode("utf-8")
    api_request = request.Request(url=url, method="POST", data=body, headers=request_headers)

    try:
        with request.urlopen(api_request, timeout=15) as response:
            status_code = getattr(response, "status", response.getcode())
            if not 200 <= int(status_code) < 300:
                raise ValueError(f"Email API request failed with status {status_code}")
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        logger.error("Email API HTTP error (%s): %s", exc.code, detail)
        raise ValueError("Email API request failed") from exc
    except error.URLError as exc:
        logger.error("Email API connection error: %s", exc.reason)
        raise ValueError("Email API request failed") from exc