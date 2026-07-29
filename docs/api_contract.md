# API Contract — Micro Learning Challenge App

This document summarizes the HTTP API surface, auth requirements, request/response shapes, and key integration notes for frontend developers.

Base URL: `/` (API root available at `/api/`)
All API endpoints referenced under `/api/...` unless full path shown.

Authentication
- Header: `Authorization: Bearer <access_token>` for protected endpoints.
- Login: `POST /api/auth/login/`
  - Body: `{ "username": "...", "password": "..." }`
  - 200: `{ "access": "<jwt>", "refresh": "<jwt>", "user": {"id":..,"username":...,"email":...,"role":...} }`
- Refresh: `POST /api/auth/token/refresh/` `{ "refresh": "<refresh_token>" }` → `{ "access": "<jwt>" }`
- Register: `POST /api/auth/register/` `{ "username","email","password" }` → 201
- Logout: `POST /api/auth/logout/` `{ "refresh": "<refresh_token>" }` → 200
- Password reset flows: `POST /api/auth/password/forgot/`, `POST /api/auth/password/reset/confirm/`

Common
- Pagination: `page`, `page_size` (standard list responses contain `count`, `next`, `previous`, `results`).
- Trailing slashes: none (`TRAILING_SLASH = False`).
- Caching: GET endpoints may be cached by namespace (see specific endpoints).

Endpoints

Categories
- `GET /api/categories/`
  - Query: `search`, `sort_by`
  - Response item: `{ id, name, slug, description, icon, module_count }`
- `POST /api/categories/` (admin)
- `GET /api/categories/<id>/`

Modules
- `GET /api/modules/`
  - Query: `category_id`, `search`, `sort_by`
  - Response item fields include computed learning state: `module_action` (`enroll`|`resume`|`start`|`coming_soon`), `module_progress_percent`, `module_completed_parts`, `module_total_parts`.
- `POST /api/modules/` (admin)
- `POST /api/modules/<id>/enroll/` — enroll current user
  - Response: `{ module_id, enrolled: true, enrolled_at, created }`

Lessons
- `GET /api/lessons/` (query `module_id`)
- `GET /api/lessons/<id>/?include=knowledge_check`
  - `knowledge_check` (optional) shape:
    ```json
    {
      "challenge_id": int,
      "title": "...",
      "description": "...",
      "difficulty": "easy|medium|hard",
      "points": int,
      "time_limit_minutes": int,
      "question": { /* ChallengeQuestionPublic */ },
      "attempt": { /* partial attempt summary or null */ }
    }
    ```

Challenges (Assessment)
- `GET /api/challenges/` — list
  - Query: `lesson_id`, `module_id`, `category_id`, `difficulty`, `search`, `sort_by`
  - Item: `{ id, title, description, difficulty, points, time_limit_minutes, scope }`
- `GET /api/challenges/<id>/` — detail
  - Admins: full questions w/ correct answers; Learners: public question format
- `POST /api/challenges/<challenge_id>/progress/` — save partial answers
  - Body: `{ "answers": [ { "question_id": int, "answer_text"?, "answer_options"?, "answer_number"?, "answer_boolean"? }, ... ] }`
  - Response: `ChallengeAttempt` object:
    ```json
    {
      "id": int,
      "challenge": int,
      "challenge_title": "...",
      "started_at": "...",
      "deadline_at": "...",
      "last_saved_at": "...",
      "is_submitted": false,
      "submitted_at": null,
      "total_score": 0,
      "points_awarded": 0,
      "is_within_time_limit": true,
      "completion_time_seconds": null,
      "submission_timing_status": "not_submitted",
      "answers": [ { "question", "question_text", "question_type", "submitted_answer" }, ... ]
    }
    ```
- `POST /api/challenges/<challenge_id>/submit/` — final submission & grading
  - Headers: optional `X-Idempotency-Key: <uuid>`
  - Body: same as progress save
  - Grading rules summary:
    - `single_choice`, `true_false`: normalized exact match
    - `multiple_choice`: unordered set equality
    - `numeric`: match within question `numeric_tolerance`
    - `short_text_strict`: whitespace-normalized exact match
  - Success response: `ChallengeSubmissionResult` (attempt-level) includes per-answer `correct_answer_value`, `score`, and `explanation`:
    ```json
    {
      "id": int,
      "challenge": int,
      "challenge_title": "...",
      "started_at": "...",
      "deadline_at": "...",
      "is_submitted": true,
      "submitted_at": "...",
      "total_score": 80,
      "points_awarded": 10,
      "is_within_time_limit": true,
      "completion_time_seconds": 120,
      "submission_timing_status": "on_time",
      "answers": [
        { "question": id, "question_text": "...", "question_type": "...", "submitted_answer": ..., "correct_answer_value": ..., "score": int, "explanation": "..." }
      ]
    }
    ```
  - Side-effects: creates `ChallengeSubmission`, awards points (`PointTransaction`), updates `UserProgress` (lesson/module), updates daily activity and user profile totals.
- `GET /api/challenges/submissions/me/` — user's submissions

Daily Challenges
- Same behaviors under `/api/daily-challenges/`
- `GET /api/daily-challenges/today/?date=YYYY-MM-DD` — fetch daily challenge for date

Quizzes
- `GET /api/quiz/quizzes/?lesson_id=...` — list user quizzes
- `GET /api/quiz/quizzes/<id>/` — detail with questions and answers
- `POST /api/quiz/quizzes/<id>/submit/` — submit answers
  - Body: `{ "answers": [ { "question_id": int, "answer_id": int } | { "question_id": int, "answer_ids": [int,...] } ] }`
  - Response: `{ "total_questions": int, "correct_answers": int, "score": 100, "results": [ { question_id, question_type, selected_answers, is_correct, correct_answers, explanation } ] }`
  - Side-effects: creates/updates `QuizSubmission`; triggers `UserProgress.sync_module_progress` when applicable

Progress
- `GET /api/progress/` — list current user's progress entries
  - Query: `owner_type=challenge|lesson|module`, `completed=true|false`
- `GET /api/progress/summary/` — aggregated summary for user `{ challenges:{...}, lessons:{...}, modules:{...}, points_earned }`
- Admin endpoints: `/api/progress/admin/` and `/api/progress/admin/summary/`

Points
- `GET /api/points/admin/transactions/` — list point transactions (admin)
  - Query: `user_id`, `source_type`, `source_id`

Notifications
- `GET /api/notifications/?is_read=true|false` — list user notifications
  - Response items include computed `day_bucket` (`today`|`yesterday`|`earlier`), `day_tag`, `day_date`
  - Response contains top-level `unread_count` in list response
- `POST /api/notifications/<id>/read/` — mark read
- `POST /api/notifications/read-all/` — mark all read

Users / Profile
- `GET/PUT /api/auth/profile/` — get and update current user profile
  - `PUT` supports multipart form for `profile_picture` and `bio` fields
  - Response includes `profile` nested and `knowledge_momentum` series
- Admin user management: `GET /api/auth/users/`, `GET /api/auth/users/<id>/`, `PATCH /api/auth/users/<id>/role/` (protects demoting last admin)

Examples

Challenge submit example request:
```json
POST /api/challenges/42/submit/
Headers: Authorization: Bearer <token>, X-Idempotency-Key: abc-123
Body:
{
  "answers": [
    {"question_id": 101, "answer_text": "option_a"},
    {"question_id": 102, "answer_options": ["opt1", "opt3"]},
    {"question_id": 103, "answer_number": 12.5},
    {"question_id": 104, "answer_boolean": true}
  ]
}
```

Quiz submit example request:
```json
POST /api/quiz/quizzes/7/submit/
Headers: Authorization: Bearer <token>
Body:
{
  "answers": [
    {"question_id": 1, "answer_id": 5},
    {"question_id": 2, "answer_ids": [9,10]}
  ]
}
```

Integration notes
- Use `X-Idempotency-Key` for challenge submits to avoid duplicate grading on retries.
- `ChallengeQuestionPublicSerializer` includes `answer_format` to guide frontend payload fields (`answer_text`, `answer_options`, `answer_number`, `answer_boolean`).
- Cached GET endpoints may return stale data until admin changes invalidate the namespace — frontend should expect eventual consistency after admin updates.
- Use `include=knowledge_check` on lesson detail to surface a single inline practice question.

References (server code):
- Challenges: `backend/apps/challenges/` (views + serializers + models)
- Quizzes: `backend/apps/quiz/` (views + serializers + models)
- Progress: `backend/apps/progress/` (models + views)
- Users: `backend/apps/users/` (serializers + views + models)

---
Generated by developer tooling for frontend integration. If you want this exported as OpenAPI (YAML/JSON) or Postman collection, I can generate that next.