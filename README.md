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