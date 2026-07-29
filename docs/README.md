# Micro Learning Challenge App

A Django REST API for micro-learning experiences with authentication, guided learning content, challenges, daily challenges, progress tracking, points, notifications, and quiz management.

## Highlights

- JWT-based authentication and password reset flow
- Learner profile data with streak and knowledge momentum tracking
- Category, module, lesson, challenge, and daily challenge APIs
- Progress summaries for learners and admins
- Points ledger and notification panel endpoints
- Quiz APIs for both learners and administrators
- PostgreSQL-ready deployment with SQLite support for local development

## Tech Stack

- Django 6
- Django REST Framework
- SimpleJWT
- PostgreSQL for production, SQLite for local development
- WhiteNoise for static file serving
- Resend for transactional email
- pytest and pytest-django for tests

## Project Structure

```text
Micro_Learning_Challenge_App-/
├── backend/
│   ├── apps/
│   │   ├── categories/
│   │   ├── challenges/
│   │   ├── daily_challenge/
│   │   ├── lessons/
│   │   ├── modules/
│   │   ├── notifications/
│   │   ├── points/
│   │   ├── progress/
│   │   ├── quiz/
│   │   └── users/
│   └── config/
├── docs/
│   └── api.md
├── DEPLOYMENT.md
├── requirements.txt
├── render.yaml
└── README.md
```

## Getting Started

1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Configure the backend environment variables for your local setup.
4. Run database migrations from the `backend/` directory.
5. Start the development server.

Example:

```bash
cd backend
python manage.py migrate
python manage.py runserver
```

## Testing

Run the backend test suite from the `backend/` directory:

```bash
pytest tests/ -v
```

## Documentation

- API reference: [docs/api.md](docs/api.md)
- Deployment guide: [DEPLOYMENT.md](DEPLOYMENT.md)

## Notes

- The API root responds at `/` with a health check payload.
- Route prefixes begin under `/api/` for the main application surface.
- Production setup details and environment variables are documented in [DEPLOYMENT.md](DEPLOYMENT.md).
