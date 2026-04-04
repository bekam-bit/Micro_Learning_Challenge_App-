# Micro_Learning_Challenge_App-

## Combined Sample Data (Categories + Modules + Lessons)

Note:
- User and admin use the same categories/modules/lessons endpoints.
- Difference is by token role:
	- user (public read or learner token)
	- admin (admin JWT for write operations)

### Categories Sample

User list request:

```http
GET /api/categories/?search=python&sort_by=display_order&page=1&page_size=12
```

Response:

```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 1,
			"name": "Python Basics",
			"slug": "python-basics",
			"description": "Fundamentals of Python programming.",
			"icon": "code",
			"module_count": 2
		},
		{
			"id": 2,
			"name": "Web Development",
			"slug": "web-development",
			"description": "Backend API and Django essentials.",
			"icon": "globe",
			"module_count": 1
		}
	]
}
```

Admin create request:

```http
POST /api/categories/
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
	"name": "Data Structures",
	"slug": "data-structures",
	"description": "Arrays, linked lists, stacks, queues.",
	"icon": "layers",
	"display_order": 3,
	"is_active": true
}
```

### Modules Sample

User list request:

```http
GET /api/modules/?category_id=1&search=intro&sort_by=title&page=1&page_size=12
```

Response:

```json
{
	"count": 1,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 10,
			"category": 1,
			"title": "Intro to Variables",
			"description": "Learn variables and data types.",
			"status": "active",
			"level": "beginner",
			"estimated_time": 20,
			"prerequisites": [],
			"module_action": "enroll",
			"module_progress_percent": 0,
			"module_completed_parts": 0,
			"module_total_parts": 0,
			"created_at": "2026-04-04T08:30:00Z",
			"updated_at": "2026-04-04T08:30:00Z"
		}
	]
}
```

User enroll request:

```http
POST /api/modules/10/enroll/
Authorization: Bearer <learner_token>
```

Response:

```json
{
	"module_id": 10,
	"enrolled": true,
	"enrolled_at": "2026-04-04T09:00:00Z",
	"created": true
}
```

Admin create request:

```http
POST /api/modules/
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
	"category": 1,
	"title": "Functions 101",
	"description": "Defining and calling functions.",
	"status": "active",
	"level": "beginner",
	"estimated_time": 30
}
```

### Lessons Sample

User list request:

```http
GET /api/lessons/?module_id=10&page=1&page_size=12
```

Response:

```json
{
	"count": 2,
	"next": null,
	"previous": null,
	"results": [
		{
			"id": 101,
			"title": "What is a Variable?",
			"content": "<p>Variables store values...</p>",
			"video_url": "https://cdn.example.com/videos/variable-intro.mp4",
			"video_file": null,
			"order": 1,
			"category": 1,
			"module": 10,
			"created_at": "2026-04-04T09:00:00Z",
			"updated_at": "2026-04-04T09:00:00Z"
		},
		{
			"id": 102,
			"title": "Primitive Data Types",
			"content": "<p>Integer, float, string, boolean...</p>",
			"video_url": "https://cdn.example.com/videos/data-types.mp4",
			"video_file": null,
			"order": 2,
			"category": 1,
			"module": 10,
			"created_at": "2026-04-04T09:05:00Z",
			"updated_at": "2026-04-04T09:05:00Z"
		}
	]
}
```

Admin create request:

```http
POST /api/lessons/
Authorization: Bearer <admin_token>
Content-Type: application/json
```

```json
{
	"title": "Function Basics",
	"content": "<p>A function is a reusable block of code...</p>",
	"video_url": "https://cdn.example.com/videos/function-basics.mp4",
	"order": 1,
	"category": 1,
	"module": 12
}
```

Validation rule for lessons:
- At least one of `video_url` or `video_file` must be provided.
