# API Reference

This document covers the public backend API for Micro Learning Challenge App.

## Overview

- Base URL prefixes all application routes with `/api/`.
- The API root is `/` and returns a simple health response.
- Authentication uses JWT access and refresh tokens.
- Protected endpoints expect `Authorization: Bearer <access_token>`.
- Most list endpoints use page-number pagination with `page` and `page_size`.
- Admin-only endpoints are marked as such in the tables below.

### Root Health Check

| Endpoint | Method | Auth | Description |
| --- | --- | --- | --- |
| `/` | `GET` | No | Returns `{ "message": "Micro Learning Challenge API is running", "status": "healthy" }`. |

### Route Groups

| Prefix | Purpose |
| --- | --- |
| `/api/auth/` | Authentication, profile, and user administration |
| `/api/categories/` | Learning categories |
| `/api/modules/` | Learning modules and enrollment |
| `/api/lessons/` | Lessons |
| `/api/challenges/` | Challenge content, questions, progress, and submission |
| `/api/daily-challenges/` | Daily challenge content, questions, progress, and submission |
| `/api/progress/` | Progress dashboards and summaries |
| `/api/points/` | Points ledger |
| `/api/notifications/` | User notifications |
| `/api/quiz/` | Quiz routes exposed through routers |

## Authentication

### Endpoints

| Endpoint | Method | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/auth/register/` | `POST` | No | Any | Register a new user. |
| `/api/auth/login/` | `POST` | No | Any | Obtain access and refresh tokens plus the user object. |
| `/api/auth/token/` | `POST` | No | Any | Alias for login. |
| `/api/auth/token/refresh/` | `POST` | No | Any | Exchange a refresh token for a new access token. |
| `/api/auth/logout/` | `POST` | Yes | Authenticated | Blacklist a refresh token. |
| `/api/auth/password/forgot/` | `POST` | No | Any | Request a password reset email. |
| `/api/auth/password/reset/confirm/` | `POST` | No | Any | Confirm a password reset using `uid` and `token`. |
| `/api/auth/profile/` | `GET` | Yes | Authenticated | Return the current user profile, streak, and knowledge momentum. |
| `/api/auth/profile/` | `PATCH` | Yes | Authenticated | Update profile and selected user fields. |
| `/api/auth/users/` | `GET` | Yes | Admin | List users for admin management. |
| `/api/auth/users/<id>/` | `GET` | Yes | Admin | Retrieve a single user. |
| `/api/auth/users/<id>/role/` | `PATCH` | Yes | Admin | Update a user's role. |

### Common Request Fields

`POST /api/auth/register/`
- `username` required string
- `email` required unique email
- `password` required string, minimum length 8

`POST /api/auth/login/` and `/api/auth/token/`
- `username` required string
- `password` required string

`POST /api/auth/token/refresh/`
- `refresh` required string

`POST /api/auth/logout/`
- `refresh` required string

`POST /api/auth/password/forgot/`
- `email` required email

`POST /api/auth/password/reset/confirm/`
- `uid` required string
- `token` required string
- `new_password` required string, minimum length 8
- `confirm_password` required string, must match `new_password`

`PATCH /api/auth/users/<id>/role/`
- `role` required enum: `admin` or `learner`

### Response Notes

- Login and token endpoints return `access`, `refresh`, and a nested `user` object.
- The profile endpoint returns user fields, a nested `profile` object, and a `knowledge_momentum` object.
- User list and user detail endpoints expose completion counters such as `total_modules_completed`, `total_lessons_completed`, and `total_quizzes_completed`.
- Password reset responses are intentionally generic to avoid account enumeration.

## Categories

### Endpoints

| Endpoint | Method(s) | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/categories/` | `GET` | Yes | Authenticated | List categories. Non-admin users only see active categories. |
| `/api/categories/` | `POST` | Yes | Admin | Create a category. |
| `/api/categories/<id>/` | `GET` | Yes | Authenticated | Retrieve one category with related module summaries. |
| `/api/categories/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a category. |

### Query Params

- `search` for case-insensitive name filtering
- `sort_by` for ordering by `name`, `display_order`, or `created_at`
- `page` and `page_size` for pagination

### Common Fields

- `name`
- `slug`
- `description`
- `icon`
- `display_order`
- `is_active`

## Modules

### Endpoints

| Endpoint | Method(s) | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/modules/` | `GET` | Yes | Authenticated | List modules. |
| `/api/modules/` | `POST` | Yes | Admin | Create a module. |
| `/api/modules/<id>/` | `GET` | Yes | Authenticated | Retrieve one module. |
| `/api/modules/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a module. |
| `/api/modules/<id>/enroll/` | `POST` | Yes | Authenticated | Enroll the current user in a module. |

### Query Params

- `category_id`
- `search`
- `sort_by`
- `page` and `page_size`

### Common Fields

- `category`
- `title`
- `description`
- `status`
- `level`
- `estimated_time`
- `prerequisites`

### Enrollment Response

The enroll endpoint returns a payload that includes `module_id`, `enrolled`, `enrolled_at`, and `created`.

## Lessons

### Endpoints

| Endpoint | Method(s) | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/lessons/` | `GET` | Yes | Authenticated | List lessons. |
| `/api/lessons/` | `POST` | Yes | Admin | Create a lesson. |
| `/api/lessons/<id>/` | `GET` | Yes | Authenticated | Retrieve one lesson. |
| `/api/lessons/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a lesson. |

### Query Params

- `module_id`
- `page` and `page_size`

### Common Fields

- `title`
- `content`
- `video_url`
- `video_file`
- `order`
- `category`
- `module`

### Validation Notes

- At least one of `video_url` or `video_file` must be provided.

## Challenges

### Endpoints

| Endpoint | Method(s) | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/challenges/` | `GET` | Yes | Authenticated | List challenges. |
| `/api/challenges/` | `POST` | Yes | Admin | Create a challenge. |
| `/api/challenges/<id>/` | `GET` | Yes | Authenticated | Retrieve one challenge with nested questions. |
| `/api/challenges/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a challenge. |
| `/api/challenges/<challenge_id>/questions/` | `GET` | Yes | Authenticated | List questions for a challenge. |
| `/api/challenges/<challenge_id>/questions/` | `POST` | Yes | Admin | Create a challenge question. |
| `/api/challenges/questions/<id>/` | `GET` | Yes | Authenticated | Retrieve one question. |
| `/api/challenges/questions/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a question. |
| `/api/challenges/<challenge_id>/progress/` | `GET`, `POST` | Yes | Learner | Retrieve or save in-progress answers. |
| `/api/challenges/<challenge_id>/submit/` | `POST` | Yes | Learner | Submit answers, grade the attempt, and award points. |
| `/api/challenges/submissions/me/` | `GET` | Yes | Learner | List the current user's challenge submissions. |

### Query Params

`GET /api/challenges/`
- `scope`
- `difficulty`
- `lesson_id`
- `module_id`
- `category_id`
- `search`
- `sort_by`
- `page` and `page_size`

`GET /api/challenges/submissions/me/`
- `challenge_id`
- `page` and `page_size`

### Common Fields

Challenge fields include `title`, `description`, `difficulty`, `points`, `time_limit_minutes`, `lesson`, `module`, `category`, `scope`, and `scope_display`.

Question fields include `question_text`, `question_type`, `options`, `correct_options`, `correct_answer`, `numeric_tolerance`, `explanation`, `max_score`, and `order`.

### Submission Notes

- Submit payloads use an `answers` array.
- Supported answer keys include `answer_text`, `answer_options`, `answer_number`, and `answer_boolean`.
- `X-Idempotency-Key` may be supplied for safe retry behavior.

## Daily Challenges

### Endpoints

| Endpoint | Method(s) | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/daily-challenges/` | `GET` | Yes | Authenticated | List daily challenges. |
| `/api/daily-challenges/` | `POST` | Yes | Admin | Create a daily challenge. |
| `/api/daily-challenges/today/` | `GET` | Yes | Authenticated | Fetch today’s daily challenge or a requested date. |
| `/api/daily-challenges/<id>/` | `GET` | Yes | Authenticated | Retrieve one daily challenge with questions. |
| `/api/daily-challenges/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a daily challenge. |
| `/api/daily-challenges/<id>/questions/` | `GET` | Yes | Authenticated | List questions for a daily challenge. |
| `/api/daily-challenges/<id>/questions/` | `POST` | Yes | Admin | Create a daily challenge question. |
| `/api/daily-challenges/questions/<id>/` | `GET` | Yes | Authenticated | Retrieve one daily challenge question. |
| `/api/daily-challenges/questions/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | Admin | Update or delete a daily challenge question. |
| `/api/daily-challenges/<id>/progress/` | `GET`, `POST` | Yes | Learner | Retrieve or save in-progress answers. |
| `/api/daily-challenges/<id>/submit/` | `POST` | Yes | Learner | Submit answers for grading and scoring. |
| `/api/daily-challenges/submissions/me/` | `GET` | Yes | Learner | List the current user's daily challenge submissions. |

### Notes

- Daily challenges are date-based.
- They are not bound to a lesson, module, or category.
- The `today/` endpoint can accept an explicit `date` query parameter.

## Progress

### Endpoints

| Endpoint | Method | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/progress/` | `GET` | Yes | Authenticated | List the current user's progress records. |
| `/api/progress/summary/` | `GET` | Yes | Authenticated | Return the current user's aggregated summary. |
| `/api/progress/admin/` | `GET` | Yes | Admin | List all users' progress records. |
| `/api/progress/admin/summary/` | `GET` | Yes | Admin | Return a global summary for dashboards. |

### Query Params

`GET /api/progress/`
- `owner_type`
- `completed`

`GET /api/progress/admin/`
- `page` and `page_size`
- `search`
- `ordering`
- `user_id`
- `owner_type`
- `completed`
- `from`
- `to`

`GET /api/progress/admin/summary/`
- `user_id`
- `owner_type`
- `from`
- `to`

### Response Notes

- Learner progress items include `owner_type`, `owner_id`, `owner_title`, `completed`, `points_earned`, `completed_parts`, `total_parts`, and `progress_percent`.
- Admin progress items also include `user_id`, `username`, and `email`.
- Summary payloads report challenge, lesson, and module completion statistics plus `points_earned`.

## Points

### Endpoint

| Endpoint | Method | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/points/admin/transactions/` | `GET` | Yes | Admin | List the points transaction ledger. |

### Query Params

- `page` and `page_size`
- `search`
- `ordering`
- `user_id`
- `source_type`
- `source_id`

### Common Fields

- `id`
- `user_id`
- `username`
- `email`
- `points`
- `source_type`
- `source_id`
- `reason`
- `metadata`
- `created_at`
- `updated_at`

## Notifications

### Endpoints

| Endpoint | Method | Auth | Role | Description |
| --- | --- | --- | --- | --- |
| `/api/notifications/` | `GET` | Yes | Authenticated | List the current user's notifications. |
| `/api/notifications/<id>/read/` | `POST` | Yes | Authenticated | Mark one notification as read. |
| `/api/notifications/read-all/` | `POST` | Yes | Authenticated | Mark all notifications as read. |

### Query Params

- `is_read`
- `page`
- `page_size`

### Response Notes

- List responses include `count`, `next`, `previous`, `results`, and `unread_count`.
- Notification items include `message`, `is_read`, `created_at`, `day_bucket`, `day_tag`, and `day_date`.

### Retention

Notification cleanup is driven by a Django admin retention setting with `enabled` and `retention_days` fields.

## Quiz

The quiz app is exposed through a DRF `DefaultRouter`.

### Routes

| Prefix | Purpose |
| --- | --- |
| `/api/quiz/admin/quizzes/` | Admin quiz router endpoints |
| `/api/quiz/admin/questions/` | Admin question router endpoints |
| `/api/quiz/admin/answers/` | Admin answer router endpoints |
| `/api/quiz/quizzes/` | User quiz router endpoints |

### Notes

- These routes use standard router-generated actions from the corresponding viewsets.
- Refer to the quiz serializers and viewsets in `backend/apps/quiz/` for resource-specific fields and behaviors.

## Production Notes

- The project supports SQLite locally and PostgreSQL in production.
- `backend/requirements.txt` delegates to the root `requirements.txt` file.
- Deployment-specific environment variables and guidance live in [DEPLOYMENT.md](../DEPLOYMENT.md).
- Summary endpoints may use short-lived caching in production.
- API query profiling can be enabled through Django settings for performance monitoring.

## Suggested Client Flow

1. Register or log in through `/api/auth/`.
2. Fetch the profile and progress endpoints for the current learner.
3. Load categories, modules, and lessons to drive the learning experience.
4. Submit challenge and daily challenge attempts with idempotency keys when appropriate.
5. Poll notifications and points endpoints for feedback and rewards.
