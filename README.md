# Micro_Learning_Challenge_App-

Backend API reference organized in the requested order.

Base route prefixes:
- `/api/auth/`
- `/api/categories/`
- `/api/modules/`
- `/api/lessons/`
- `/api/challenges/`
- `/api/daily-challenges/`
- `/api/quiz/`
- `/api/progress/`
- `/api/points/`

Authentication:
- JWT Bearer token for protected endpoints.
- Header format: `Authorization: Bearer <access_token>`
- Access policy for app features: authenticated users can access feature APIs; admin-only endpoints are explicitly marked in Role Required.

Pagination:
- List endpoints that use pagination follow page-number pagination.
- Default `page_size` is `12`, max `page_size` is `100`.

## 1. Auth

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/auth/register/` | `POST` | No | Any | Register a new user. Creates a profile automatically. |
| `/api/auth/login/` | `POST` | No | Any | Obtain access + refresh token pair and user object. |
| `/api/auth/token/` | `POST` | No | Any | Alias of login endpoint (same serializer as login). |
| `/api/auth/token/refresh/` | `POST` | No | Any | Exchange refresh token for a new access token. |
| `/api/auth/logout/` | `POST` | Yes | Authenticated | Blacklist refresh token. |
| `/api/auth/users/` | `GET` | Yes | Admin | List users for admin panel. |
| `/api/auth/users/<id>/` | `GET` | Yes | Admin | Retrieve one user for admin panel. |
| `/api/auth/users/<id>/role/` | `PATCH` | Yes | Admin | Update user role (`admin` or `learner`). |

### Request Fields

`POST /api/auth/register/`
- `username` string required
- `email` email required and unique
- `password` string required, min length 8

`POST /api/auth/login/` and `POST /api/auth/token/`
- `username` string required
- `password` string required

`POST /api/auth/token/refresh/`
- `refresh` string required

`POST /api/auth/logout/`
- `refresh` string required

`PATCH /api/auth/users/<id>/role/`
- `role` enum required: `admin` or `learner`

### Response Fields

Register response fields:
- `id`, `username`, `email`, `role`, `date_joined`

Login/token response fields:
- `access`, `refresh`
- `user`: `id`, `username`, `email`, `role`

Logout response fields:
- `detail`

User list item fields:
- `id`, `username`, `email`, `role`, `is_active`, `date_joined`
- `total_modules_completed`, `total_lessons_completed`, `total_quizzes_completed`

### Sample

Request:
```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
	"username": "demo_learner",
	"password": "SecurePass123"
}
```

Response:
```json
{
	"refresh": "<jwt_refresh_token>",
	"access": "<jwt_access_token>",
	"user": {
		"id": 7,
		"username": "demo_learner",
		"email": "demo@example.com",
		"role": "learner"
	}
}
```

## 2. Profile and Streak

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/auth/profile/` | `GET` | Yes | Authenticated | Get current user profile with knowledge momentum and streak fields. |
| `/api/auth/profile/` | `PATCH` | Yes | Authenticated | Update username/email and profile fields (including `bio` and `profile_picture`). |

### Query Params

`GET /api/auth/profile/`
- `year` optional integer, defaults to current year. Used for `knowledge_momentum` range.

### Request Fields

`PATCH /api/auth/profile/`
- User fields:
	- `username` optional string
	- `email` optional email
- Profile fields:
	- `bio` optional string
	- `profile_picture` optional file

### Response Fields

Top-level fields:
- `id`, `username`, `email`, `role`, `date_joined`
- `profile`
- `knowledge_momentum`
- `total_modules_completed`, `total_lessons_completed`, `total_quizzes_completed`

`profile` fields:
- `bio`
- `profile_picture`
- `total_points`
- `total_points_earned`
- `modules_completed_count`, `modules_total_count`, `modules_completion_percentage`
- `lessons_completed_count`, `lessons_total_count`, `lessons_completion_percentage`
- `challenges_completed_count`, `challenges_total_count`, `challenges_completion_percentage`
- `current_streak`, `max_streak`, `last_activity_date`

`knowledge_momentum` fields:
- `year`, `from`, `to`, `active_days`, `total_score`
- `days[]` with `date`, `score`, `level`

### Sample

Request:
```http
GET /api/auth/profile/?year=2026
Authorization: Bearer <access_token>
```

Response:
```json
{
	"id": 7,
	"username": "demo_learner",
	"email": "demo@example.com",
	"role": "learner",
	"date_joined": "2026-03-15T08:30:00Z",
	"profile": {
		"bio": "Learning every day",
		"profile_picture": "/media/profile_pictures/demo.png",
		"total_points": 120,
		"total_points_earned": 120,
		"modules_completed_count": 2,
		"modules_total_count": 5,
		"modules_completion_percentage": 40.0,
		"lessons_completed_count": 8,
		"lessons_total_count": 20,
		"lessons_completion_percentage": 40.0,
		"challenges_completed_count": 6,
		"challenges_total_count": 12,
		"challenges_completion_percentage": 50.0,
		"current_streak": 4,
		"max_streak": 9,
		"last_activity_date": "2026-04-05"
	},
	"knowledge_momentum": {
		"year": 2026,
		"from": "2026-01-01",
		"to": "2026-04-05",
		"active_days": 28,
		"total_score": 180,
		"days": [
			{"date": "2026-04-03", "score": 10, "level": 1},
			{"date": "2026-04-04", "score": 30, "level": 2},
			{"date": "2026-04-05", "score": 40, "level": 2}
		]
	},
	"total_modules_completed": 2,
	"total_lessons_completed": 8,
	"total_quizzes_completed": 5
}
```

Admin user detail response (`GET /api/auth/users/<id>/`) uses the same shape as user list items, including:
- `id`, `username`, `email`, `role`, `is_active`, `date_joined`
- `total_modules_completed`, `total_lessons_completed`, `total_quizzes_completed`

## 3. Categories

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/categories/` | `GET` | Yes | Authenticated | List categories. Non-admin gets only active categories. |
| `/api/categories/` | `POST` | Yes | Admin | Create category. |
| `/api/categories/<id>/` | `GET` | Yes | Authenticated | Retrieve category detail with nested module summaries. |
| `/api/categories/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete category. |

### Query Params

`GET /api/categories/`
- `search` optional string, case-insensitive category name search
- `sort_by` optional enum: `name`, `-name`, `display_order`, `-display_order`, `created_at`, `-created_at`
- `page`, `page_size` optional pagination params

### Request Fields

Write payload (`POST`, `PUT`, `PATCH`):
- `name` string required on create
- `slug` string optional
- `description` string required on create
- `icon` string optional, default `category`
- `display_order` integer optional, default `0`
- `is_active` boolean optional, default `true`

### Response Fields

List item fields:
- `id`, `name`, `slug`, `description`, `icon`, `module_count`

Detail fields:
- `id`, `name`, `slug`, `description`, `icon`
- `modules[]`: `id`, `title`, `description`

### Sample

Request:
```http
GET /api/categories/?search=python&sort_by=display_order&page=1&page_size=12
```

Response:
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"name": "Python Basics",
			"slug": "python-basics",
			"description": "Core Python fundamentals",
			"icon": "code",
			"module_count": 3
		}
	]
}
```

## 4. Modules

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/modules/` | `GET` | Yes | Authenticated | List modules with learner card state fields. |
| `/api/modules/` | `POST` | Yes | Admin | Create module. |
| `/api/modules/<id>/` | `GET` | Yes | Authenticated | Retrieve one module. |
| `/api/modules/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete module. |
| `/api/modules/<id>/enroll/` | `POST` | Yes | Authenticated | Enroll current user in module. |

### Query Params

`GET /api/modules/`
- `category_id` optional integer
- `search` optional string (title contains)
- `sort_by` optional enum: `title`, `-title`, `created_at`, `-created_at`, `updated_at`, `-updated_at`
- `page`, `page_size` optional pagination params

### Request Fields

Write payload (`POST`, `PUT`, `PATCH`):
- `category` integer required on create
- `title` string required on create
- `description` string required on create
- `status` enum optional: `active`, `inactive`, `coming_soon`
- `level` enum optional: `beginner`, `intermediate`, `expert`
- `estimated_time` integer optional (minutes)
- `prerequisites` many-to-many relation (read-only in serializer response)

### Response Fields

Module fields:
- `id`, `category`, `title`, `description`
- `status`, `level`, `estimated_time`, `prerequisites`
- `module_action` enum: `enroll`, `start`, `resume`, `coming_soon`
- `module_progress_percent`, `module_completed_parts`, `module_total_parts`
- `created_at`, `updated_at`

Enroll response fields:
- `module_id`, `enrolled`, `enrolled_at`, `created`

### Sample

Request:
```http
POST /api/modules/10/enroll/
Authorization: Bearer <access_token>
```

Response:
```json
{
	"module_id": 10,
	"enrolled": true,
	"enrolled_at": "2026-04-05T10:00:00Z",
	"created": true
}
```

## 5. Lessons

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/lessons/` | `GET` | Yes | Authenticated | List lessons (optional filter by module). |
| `/api/lessons/` | `POST` | Yes | Admin | Create lesson. |
| `/api/lessons/<id>/` | `GET` | Yes | Authenticated | Retrieve lesson detail. |
| `/api/lessons/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete lesson. |

### Query Params

`GET /api/lessons/`
- `module_id` optional integer
- `page`, `page_size` optional pagination params

### Request Fields

Write payload (`POST`, `PUT`, `PATCH`):
- `title` string required on create
- `content` string required on create
- `video_url` URL optional
- `video_file` file optional
- `order` integer optional, default `0`
- `category` integer required on create
- `module` integer optional/null allowed

Validation:
- At least one of `video_url` or `video_file` is required.

### Response Fields

Lesson fields:
- `id`, `title`, `content`, `video_url`, `video_file`
- `order`, `category`, `module`
- `created_at`, `updated_at`

### Sample

Request:
```http
POST /api/lessons/
Authorization: Bearer <admin_access_token>
Content-Type: application/json
```

```json
{
	"title": "Variables and Data Types",
	"content": "<p>Learn how variables store data in Python.</p>",
	"video_url": "https://cdn.example.com/videos/variables.mp4",
	"order": 1,
	"category": 1,
	"module": 10
}
```

Response:
```json
{
	"id": 101,
	"title": "Variables and Data Types",
	"content": "<p>Learn how variables store data in Python.</p>",
	"video_url": "https://cdn.example.com/videos/variables.mp4",
	"video_file": null,
	"order": 1,
	"category": 1,
	"module": 10,
	"created_at": "2026-04-05T10:20:00Z",
	"updated_at": "2026-04-05T10:20:00Z"
}
```

## 6. Challenges

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/challenges/` | `GET` | Yes | Authenticated | List challenges. |
| `/api/challenges/` | `POST` | Yes | Admin | Create challenge. |
| `/api/challenges/<id>/` | `GET` | Yes | Authenticated | Challenge detail with nested questions (role-aware question fields). |
| `/api/challenges/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete challenge. |
| `/api/challenges/<challenge_id>/questions/` | `GET` | Yes | Authenticated | List questions of challenge. |
| `/api/challenges/<challenge_id>/questions/` | `POST` | Yes | Admin | Create question. |
| `/api/challenges/questions/<id>/` | `GET` | Yes | Authenticated | Retrieve question detail. |
| `/api/challenges/questions/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete question. |
| `/api/challenges/<challenge_id>/progress/` | `GET` | Yes | Learner | Get saved attempt/progress for current learner. |
| `/api/challenges/<challenge_id>/progress/` | `POST` | Yes | Learner | Save/update in-progress answers. |
| `/api/challenges/<challenge_id>/submit/` | `POST` | Yes | Learner | Final submit + grading + points. |
| `/api/challenges/submissions/me/` | `GET` | Yes | Learner | List current learner submissions. |

### Query Params

`GET /api/challenges/`
- `scope` optional enum: `lesson`, `module`, `category`
- `difficulty` optional enum: `easy`, `medium`, `hard`
- `lesson_id`, `module_id`, `category_id` optional integers
- `search` optional string
- `sort_by` optional enum: `title`, `-title`, `points`, `-points`, `difficulty`, `-difficulty`, `created_at`, `-created_at`
- `page`, `page_size` optional pagination params

`GET /api/challenges/submissions/me/`
- `challenge_id` optional integer
- `page`, `page_size` optional pagination params

### Request Fields

Challenge write payload (`POST`, `PUT`, `PATCH`):
- `title` string required on create
- `description` string required on create
- `difficulty` enum required on create: `easy`, `medium`, `hard`
- `points` integer optional, default `10`
- `time_limit_minutes` integer optional, default `30`
- Exactly one owner required:
	- `lesson` integer or null
	- `module` integer or null
	- `category` integer or null

Question write payload (`POST`, `PUT`, `PATCH`):
- `question_text` string required
- `question_type` enum required:
	- `single_choice`
	- `multiple_choice`
	- `true_false`
	- `numeric`
	- `short_text_strict`
- `options` array of strings (required for choice types)
- `correct_options` array of strings (required for multiple_choice)
- `correct_answer` string
- `numeric_tolerance` number for numeric questions
- `explanation` string optional
- `max_score` integer optional default `1`
- `order` integer optional default `0`

Progress/submit payload (`POST /progress/` and `POST /submit/`):
- `answers` array required
- `answers[].question_id` integer required
- Optional answer value fields (send only what matches question type):
	- `answer_text` string
	- `answer_options` string array
	- `answer_number` number
	- `answer_boolean` boolean

Idempotency header for submit:
- `X-Idempotency-Key` optional string, max length `128`

### Response Fields

Challenge fields:
- `id`, `title`, `description`, `difficulty`, `points`, `time_limit_minutes`, `created_at`
- `lesson`, `module`, `category`
- `scope`, `scope_display`

Public question fields:
- `id`, `challenge`, `question_text`, `question_type`, `options`, `max_score`, `order`, `answer_format`

Admin question fields include answer-key fields in addition:
- `correct_options`, `correct_answer`, `numeric_tolerance`, `explanation`

Progress and submit responses include:
- Attempt timeline/state: `started_at`, `deadline_at`, `last_saved_at`, `is_submitted`, `submitted_at`
- Scores: `total_score`, `max_score`, `points_awarded`
- Time status: `is_within_time_limit`, `submission_timing_status`, `completion_time_seconds`
- `answers`/`results` breakdown with submitted and correct values
- `idempotency_replayed` in submit response

### Sample

Request:
```http
POST /api/challenges/5/submit/
Authorization: Bearer <access_token>
X-Idempotency-Key: submit-5-20260405-1
Content-Type: application/json
```

```json
{
	"answers": [
		{"question_id": 11, "answer_text": "B"},
		{"question_id": 12, "answer_boolean": true},
		{"question_id": 13, "answer_options": ["A", "C"]}
	]
}
```

Response:
```json
{
	"id": 41,
	"challenge": 5,
	"challenge_title": "Python Basics Challenge",
	"user": 7,
	"attempt": 22,
	"response_text": "Submitted 3 answers.",
	"status": "reviewed",
	"score": 7,
	"submitted_at": "2026-04-05T11:00:10Z",
	"updated_at": "2026-04-05T11:00:10Z",
	"is_within_time_limit": true,
	"challenge_deadline_at": "2026-04-05T11:20:00Z",
	"completion_time_seconds": 520,
	"submission_timing_status": "on_time",
	"max_score": 10,
	"within_time_limit": true,
	"deadline_at": "2026-04-05T11:20:00Z",
	"points_awarded": 35,
	"idempotency_replayed": false,
	"results": {
		"id": 22,
		"challenge": 5,
		"total_score": 7,
		"points_awarded": 35,
		"answers": [
			{
				"question": 11,
				"question_text": "What is a list in Python?",
				"question_type": "single_choice",
				"submitted_answer": "B",
				"correct_answer_value": "B",
				"score": 1,
				"explanation": "A list is an ordered mutable collection."
			}
		]
	}
}
```

## 7. Daily Challenges

Daily challenges extend challenge logic through model/view inheritance and are date-based (not bound to lesson/module/category).

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/daily-challenges/` | `GET` | Yes | Authenticated | List daily challenges with optional date filtering and sorting. |
| `/api/daily-challenges/` | `POST` | Yes | Admin | Create a daily challenge (auto-sets `is_daily=true`). |
| `/api/daily-challenges/today/` | `GET` | Yes | Authenticated | Get daily challenge for today or a requested date. |
| `/api/daily-challenges/<id>/` | `GET` | Yes | Authenticated | Retrieve one daily challenge with questions. |
| `/api/daily-challenges/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a daily challenge. |
| `/api/daily-challenges/<id>/questions/` | `GET` | Yes | Authenticated | List questions for a daily challenge. |
| `/api/daily-challenges/<id>/questions/` | `POST` | Yes | Admin | Add question to a daily challenge. |
| `/api/daily-challenges/questions/<id>/` | `GET` | Yes | Authenticated | Retrieve one question. |
| `/api/daily-challenges/questions/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a question. |
| `/api/daily-challenges/<id>/progress/` | `GET`, `POST` | Yes | Learner | Save/retrieve in-progress answers. |
| `/api/daily-challenges/<id>/submit/` | `POST` | Yes | Learner | Submit answers for grading and scoring. |
| `/api/daily-challenges/submissions/me/` | `GET` | Yes | Learner | List current learner's daily challenge submissions. |

### Rules

- Daily challenges require `date`.
- Daily challenges cannot set `lesson`, `module`, or `category`.
- Daily challenge records are isolated from regular challenge endpoints (`/api/challenges/`).

### Query Params

`GET /api/daily-challenges/`
- `difficulty` optional enum: `easy`, `medium`, `hard`
- `date` optional `YYYY-MM-DD`
- `search` optional string (title contains)
- `sort_by` optional enum: `date`, `-date`, `title`, `-title`, `points`, `-points`, `created_at`, `-created_at`

`GET /api/daily-challenges/today/`
- `date` optional `YYYY-MM-DD`; if omitted, backend resolves to current local date

`GET /api/daily-challenges/submissions/me/`
- `challenge_id` optional integer filter

## 8. Progress

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/progress/` | `GET` | Yes | Authenticated | List current user's progress records. |
| `/api/progress/summary/` | `GET` | Yes | Authenticated | Get current user's aggregated progress summary. |
| `/api/progress/admin/` | `GET` | Yes | Admin | List all users' progress records. |
| `/api/progress/admin/summary/` | `GET` | Yes | Admin | Global progress summary for dashboard/KPI usage. |

### Query Params

`GET /api/progress/`
- `owner_type` optional enum: `challenge`, `lesson`, `module`
- `completed` optional boolean-like values: `true/false`, `1/0`, `yes/no`

`GET /api/progress/admin/`
- `page`, `page_size`
- `search` by username, email, challenge title, lesson title, module title
- `ordering` by `id`, `updated_at`, `created_at`, `points_earned`, `progress_percent`, `completed_parts`, `total_parts`, `user__username`
- `user_id` optional integer
- `owner_type` optional enum: `challenge`, `lesson`, `module`
- `completed` optional boolean-like values
- `from` and `to` optional date/time filters for `updated_at` (ISO datetime or `YYYY-MM-DD`)

`GET /api/progress/admin/summary/`
- `user_id`, `owner_type`, `from`, `to`

Cache and freshness behavior (when enabled):
- Summary endpoints can be cached for short TTL in production.
- Cache namespaces are invalidated on progress create/update/delete, so summary reads stay fresh.

### Response Fields

Learner progress item fields:
- `id`, `owner_type`, `owner_id`, `owner_title`
- `completed`, `points_earned`, `completed_parts`, `total_parts`, `progress_percent`
- `created_at`, `updated_at`
- `challenge`, `lesson`, `module`

Admin progress item adds:
- `user_id`, `username`, `email`

Summary payload fields:
- `challenges`: `completed`, `total`, `percentage`
- `lessons`: `completed`, `total`, `percentage`
- `modules`: `completed`, `total`, `percentage`
- `points_earned`
- `users_tracked` on admin summary endpoint

### Sample

Request:
```http
GET /api/progress/admin/?owner_type=challenge&completed=true&page=1&page_size=12
Authorization: Bearer <admin_access_token>
```

Response:
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"user_id": 7,
			"username": "demo_learner",
			"email": "demo@example.com",
			"id": 90,
			"owner_type": "challenge",
			"owner_id": 5,
			"owner_title": "Python Basics Challenge",
			"completed": true,
			"points_earned": 35,
			"completed_parts": 10,
			"total_parts": 10,
			"progress_percent": 100,
			"created_at": "2026-04-05T11:00:10Z",
			"updated_at": "2026-04-05T11:00:10Z",
			"challenge": 5,
			"lesson": null,
			"module": null
		}
	]
}
```

## Production Optimization Notes

### DB Indexes

Added for quiz submission filtering/access patterns:
- `quiz_submission(user, is_submitted)`
- `quiz_submission(quiz, is_submitted)`
- `quiz_submission(submitted_at)`

Migration:
- `apps/quiz/migrations/0006_quizsubmission_indexes.py`

### Summary Endpoint Caching

Settings:
- `SUMMARY_ENDPOINT_CACHE_ENABLED`
- `SUMMARY_ENDPOINT_CACHE_TTL_SECONDS`
- `API_RESPONSE_CACHE_ENABLED`

Cached endpoints:
- `GET /api/progress/summary/`
- `GET /api/progress/admin/summary/`

### Query Profiling Thresholds

Settings:
- `API_QUERY_PROFILE_ENABLED`
- `API_QUERY_PROFILE_QUERY_THRESHOLD`
- `API_QUERY_PROFILE_MS_THRESHOLD`

Behavior:
- Logs warnings when request query count or elapsed time crosses thresholds.

## 9. Points

### Endpoints

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/points/admin/transactions/` | `GET` | Yes | Admin | List points transactions ledger. |

### Query Params

`GET /api/points/admin/transactions/`
- `page`, `page_size`
- `search` by username, email, reason, source_type
- `ordering` by `id`, `points`, `created_at`, `updated_at`, `user__username`
- `user_id` optional integer
- `source_type` optional string (`challenge_attempt` currently)
- `source_id` optional integer

### Response Fields

Transaction item fields:
- `id`
- `user_id`, `username`, `email`
- `points`
- `source_type`, `source_id`
- `reason`
- `metadata`
- `created_at`, `updated_at`

### Sample

Request:
```http
GET /api/points/admin/transactions/?user_id=7&source_type=challenge_attempt&page=1&page_size=12
Authorization: Bearer <admin_access_token>
```

Response:
```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 33,
			"user_id": 7,
			"username": "demo_learner",
			"email": "demo@example.com",
			"points": 35,
			"source_type": "challenge_attempt",
			"source_id": 22,
			"reason": "Challenge submission reward",
			"metadata": {
				"challenge_id": 5,
				"attempt_id": 22
			},
			"created_at": "2026-04-05T11:00:10Z",
			"updated_at": "2026-04-05T11:00:10Z"
		}
	]
}
```

## 10. Notifications

### Frontend Hookup Endpoints

| Endpoint | Method | Auth Required | Description |
| --- | --- | --- | --- |
| `/api/notifications/` | `GET` | Yes | List current user's notifications for notification panel. |
| `/api/notifications/<id>/read/` | `POST` | Yes | Mark one notification as read. |
| `/api/notifications/read-all/` | `POST` | Yes | Mark all current user's notifications as read. |

### Notification List Query Params

`GET /api/notifications/`
- `is_read` optional boolean-like value: `true/false`, `1/0`, `yes/no`
- `page`, `page_size`

### Notification List Response Fields

Top-level response:
- `count`, `next`, `previous`, `results`
- `unread_count`

Notification item fields:
- `id`
- `message`
- `is_read`
- `created_at`
- `day_bucket`: `today` | `yesterday` | `earlier`
- `day_tag`: `Today` | `Yesterday` | `YYYY-MM-DD`
- `day_date`: `YYYY-MM-DD` (group key for UI sections)

### Sample: List Notifications

Request:
```http
GET /api/notifications/?is_read=false&page=1&page_size=12
Authorization: Bearer <access_token>
```

Response:
```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"unread_count": 2,
	"results": [
		{
			"id": 91,
			"message": "New daily challenge is available for 2026-04-05: \"Python Sprint\".",
			"is_read": false,
			"created_at": "2026-04-05T08:40:02Z",
			"day_bucket": "today",
			"day_tag": "Today",
			"day_date": "2026-04-05"
		}
	]
}
```

### Sample: Mark One As Read

Request:
```http
POST /api/notifications/91/read/
Authorization: Bearer <access_token>
```

Response:
```json
{
	"detail": "Notification marked as read."
}
```

### Sample: Mark All As Read

Request:
```http
POST /api/notifications/read-all/
Authorization: Bearer <access_token>
```

Response:
```json
{
	"detail": "All notifications marked as read.",
	"updated_count": 3
}
```

### Admin Setup: Retention Days

Retention is controlled from Django Admin using `NotificationRetentionSetting`:
- `enabled` (boolean)
- `retention_days` (N days)

Behavior:
- System auto-removes read notifications older than `retention_days`.
- Unread notifications are preserved.
- A default singleton settings row is seeded automatically by migration.