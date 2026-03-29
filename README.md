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