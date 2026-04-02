# Micro_Learning_Challenge_App-

## Backend API Endpoints Available for Integration

Base prefix: `/api/auth/`

Authentication type: JWT Bearer token

For protected endpoints, send header:

`Authorization: Bearer <access_token>`

### Auth and Profile APIs

| Endpoint | Methods | Auth Required | Description |
| --- | --- | --- | --- |
| `/api/auth/register/` | `POST` | No | Register a new learner account. Creates user and profile. |
| `/api/auth/login/` | `POST` | No | Login and receive JWT access/refresh tokens with user info and role. |
| `/api/auth/logout/` | `POST` | Yes | Logout current user by blacklisting refresh token. |
| `/api/auth/token/refresh/` | `POST` | No | Exchange valid refresh token for new access token. |
| `/api/auth/profile/` | `GET`, `PATCH` | Yes | Get/update current authenticated user profile and progress metrics. |

### Admin Authorization APIs

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/auth/users/` | `GET` | Yes | `admin` | List all users for admin management panel. |
| `/api/auth/users/<id>/role/` | `PATCH` | Yes | `admin` | Update target user role (`admin` or `learner`). |

### Profile Response Highlights

The profile endpoint includes:

- User identity data: id, username, email, role, date_joined
- Profile data: bio, picture, points, streak, completion counts and percentages
- Knowledge momentum data: year range, active days, total score, and day-by-day heatmap entries

### Current Backend Security/Control Rules

- Role-based access control is enforced for admin endpoints.
- Last active admin cannot be demoted.
- JWT authentication is enabled project-wide.
- Token blacklist is enabled for logout invalidation.
- Throttling is enabled for login and admin-sensitive actions.

### Categories APIs

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/categories/` | `GET` | No | - | List all active categories (search/sort supported). |
| `/api/categories/` | `POST` | Yes | `admin` | Create a new category. |
| `/api/categories/<id>/` | `GET` | No | - | Retrieve details for a single active category. |
| `/api/categories/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | `admin` | Update or delete a category. |

**Query Params:**
- `search`: Filter categories by name (case-insensitive).
- `sort_by`: Sort by `name`, `-name`, `display_order`, `-display_order`, `created_at`, `-created_at`.

**Response fields:**
- List: id, name, slug, description, icon, module_count
- Detail: id, name, slug, description, icon, modules[]

---

### Modules APIs

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/modules/` | `GET` | No | - | List all modules in active categories (search/sort/category filter supported). |
| `/api/modules/` | `POST` | Yes | `admin` | Create a new module. |
| `/api/modules/<id>/` | `GET` | No | - | Retrieve details for a single module (only if its category is active). |
| `/api/modules/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | `admin` | Update or delete a module. |

**Query Params:**
- `category_id`: Filter modules by category.
- `search`: Filter modules by title (case-insensitive).
- `sort_by`: Sort by `title`, `-title`, `created_at`, `-created_at`, `updated_at`, `-updated_at`.

**Response fields:**
- id, category, title, description, created_at, updated_at

---

### Lessons APIs

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/lessons/` | `GET` | No | - | List lessons (paginated, filterable by module). |
| `/api/lessons/` | `POST` | Yes | `admin` | Create a new lesson (with video upload or URL). |
| `/api/lessons/<id>/` | `GET` | No | - | Retrieve lesson details (only if module is active for non-admins). |
| `/api/lessons/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | `admin` | Update or delete a lesson. |

**Query Params:**
- `module_id`: Filter lessons by module.
- `page`, `page_size`: Pagination controls.

**Request fields (create/update):**
- `title`: Lesson title (string, required)
- `content`: Rich text or HTML content (string, required)
- `video_url`: URL to video explanation (string, optional)
- `video_file`: Video file upload (file, optional)
- `order`: Integer for lesson ordering (optional)
- `category`: Category ID (integer, required)
- `module`: Module ID (integer, required)

**Validation:**
- At least one of `video_url` or `video_file` must be provided.

**Response fields:**
- id, title, content, video_url, video_file, order, category, module, created_at, updated_at

**Notes:**
- Only lessons in active modules are visible to non-admin users.
- Admins can manage all lessons.
- List endpoint is paginated (default page size: 12).

---

### Challenges APIs (Frontend Contract)

Authentication:
- Public read endpoints: no auth required
- Admin write endpoints: JWT auth + `admin` role
- Learner progress/submit endpoints: JWT auth + `learner` role

#### Challenge CRUD

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/challenges/` | `GET` | No | - | List challenges (default sorted newest first). |
| `/api/challenges/` | `POST` | Yes | `admin` | Create challenge. |
| `/api/challenges/<id>/` | `GET` | No | - | Challenge detail with nested questions (role-aware fields). |
| `/api/challenges/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | `admin` | Update/delete challenge. |

Challenge list query params:
- `scope`: `lesson` | `module` | `category`
- `difficulty`: `easy` | `medium` | `hard`
- `lesson_id`, `module_id`, `category_id`
- `search`
- `sort_by`: `-created_at` (default), `created_at`, `title`, `-title`, `points`, `-points`, `difficulty`, `-difficulty`

Challenge create/update fields:
- `title` (string)
- `description` (string)
- `difficulty` (`easy`/`medium`/`hard`)
- `points` (integer)
- `time_limit_minutes` (integer)
- exactly one owner: `lesson` or `module` or `category`

#### Question CRUD (Admin)

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/challenges/<challenge_id>/questions/` | `GET` | No | - | List questions for a challenge. |
| `/api/challenges/<challenge_id>/questions/` | `POST` | Yes | `admin` | Create question with answer key config. |
| `/api/challenges/questions/<id>/` | `GET` | No | - | Get one question. |
| `/api/challenges/questions/<id>/` | `PUT`, `PATCH`, `DELETE` | Yes | `admin` | Update/delete question. |

Supported question types:
1. `single_choice`
2. `multiple_choice`
3. `true_false`
4. `numeric`
5. `short_text_strict`

Question fields:
- `question_text`
- `question_type`
- `options` (for choice types)
- `correct_options` (for multiple choice)
- `correct_answer`
- `numeric_tolerance` (for numeric)
- `explanation`
- `max_score`
- `order`

Role-aware question visibility:
- Admin question responses include answer-key fields.
- Public/learner question responses do not include answer-key fields.

#### Learner Progress + Submit

| Endpoint | Methods | Auth Required | Role Required | Description |
| --- | --- | --- | --- | --- |
| `/api/challenges/<challenge_id>/progress/` | `GET` | Yes | `learner` | Get current learner attempt and saved answers. |
| `/api/challenges/<challenge_id>/progress/` | `POST` | Yes | `learner` | Save/update progress before final submit (blocked after deadline). |
| `/api/challenges/<challenge_id>/submit/` | `POST` | Yes | `learner` | Final submit + auto-grading. |
| `/api/challenges/submissions/me/` | `GET` | Yes | `learner` | List learner submissions. |

Progress/submit payload shape:
```json
{
	"answers": [
		{
			"question_id": 123,
			"answer_text": "B",
			"answer_options": ["A", "C"],
			"answer_number": 3.14,
			"answer_boolean": true
		}
	]
}
```

Frontend should provide only the field required by the question type:
- `single_choice` -> `answer_text`
- `multiple_choice` -> `answer_options`
- `true_false` -> `answer_boolean`
- `numeric` -> `answer_number`
- `short_text_strict` -> `answer_text`

Scoring and timing behavior:
- Auto-validation happens on submit.
- Per-question score is tracked.
- Challenge points are proportional to achieved score percentage using rounded-to-nearest.
- If submitted after deadline, awarded points are `0`.

Submit response includes:
- `score`, `max_score`, `points_awarded`
- timing fields: `deadline_at`, `submitted_at`, `completion_time_seconds`, `submission_timing_status`
- per-question breakdown: `submitted_answer`, `correct_answer_value`, `score`, `explanation`

#### Idempotency (Important for frontend retries)

Submit endpoint supports idempotency header:
- `X-Idempotency-Key: <client-generated-unique-key>`

Rules:
- First submit with key -> normal processing (`201`)
- Retry with same key for same user/challenge -> replay prior result (`200`)
- Response contains `idempotency_replayed: true|false`

Recommended frontend behavior:
- Generate one key per logical submit click.
- Reuse same key for network retries of that same submit action.
- Do not generate a new key for retries.