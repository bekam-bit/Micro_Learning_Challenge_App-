# Deployment Guide

## Database Configuration

This project supports both SQLite (for local development/testing) and PostgreSQL (for production).

### Local Development (SQLite)

For local development, simply do not set the `DATABASE_URL` environment variable. The application will automatically use SQLite:

```bash
# No DATABASE_URL needed - SQLite is used by default
cp backend/.env.local.example backend/.env
```

**Benefits:**
- Zero configuration required
- Fast test execution with in-memory SQLite
- No external dependencies

### Production Deployment (NeonDB PostgreSQL)

For production, set the `DATABASE_URL` environment variable with your NeonDB connection string:

```bash
DATABASE_URL=postgresql://username:password@host.neon.tech/database_name?sslmode=require
```

**Example for Render/Other Platforms:**

1. Go to your hosting platform's environment variables settings
2. Add `DATABASE_URL` with your NeonDB connection string
3. Ensure `DJANGO_DEBUG=False` in production

**NeonDB Setup:**
1. Create a new database at https://neon.tech
2. Copy the connection string (includes SSL by default)
3. Add it to your production environment variables

## Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | NeonDB PostgreSQL connection string | `postgresql://user:pass@host.neon.tech/db?sslmode=require` |
| `DJANGO_SECRET_KEY` | Django secret key (generate with `django-admin shell` → `from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())`) | `your-secret-key` |
| `DJANGO_DEBUG` | Must be `False` in production | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed domains | `yourdomain.com,www.yourdomain.com` |
| `RESEND_API_KEY` | Email service API key | `re_xxx` |

### Optional Production Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | Empty | Frontend domains (comma-separated) |
| `SECURE_SSL_REDIRECT` | `True` (when DEBUG=False) | Force HTTPS |
| `SESSION_COOKIE_SECURE` | `True` (when DEBUG=False) | Secure cookies |
| `CSRF_COOKIE_SECURE` | `True` (when DEBUG=False) | Secure CSRF cookies |

## Quick Start

### Local Development

```bash
cd backend
cp .env.local.example .env
python manage.py migrate
python manage.py runserver
```

### Production Deployment

1. Set all required environment variables on your hosting platform
2. Run migrations: `python manage.py migrate`
3. Collect static files: `python manage.py collectstatic --noinput`
4. Start your server (platform-specific)

## Testing

Tests always use SQLite in-memory database regardless of `DATABASE_URL`:

```bash
cd backend
pytest tests/ -v
```

All 5 tests should pass.

## Security Checklist for Production

- [ ] `DJANGO_DEBUG=False`
- [ ] Strong `DJANGO_SECRET_KEY` generated
- [ ] `DATABASE_URL` points to NeonDB with SSL
- [ ] `DJANGO_ALLOWED_HOSTS` configured correctly
- [ ] `RESEND_API_KEY` or other email provider configured
- [ ] CORS origins restricted to your frontend domain
- [ ] All security headers enabled (HSTS, SSL redirect, etc.)
