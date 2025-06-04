# Backend Documentation

## Overview
The backend is built with FastAPI and provides a secure, RESTful API for user authentication, management, and report analysis. PostgreSQL is used as the database, with SQLAlchemy as the ORM and Alembic for migrations.

## Project Structure
```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes (auth, users, reports)
│   ├── core/            # Core logic (security, exceptions)
│   ├── db/              # Database setup
│   ├── models/          # SQLAlchemy models
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app entrypoint
├── requirements.txt
└── .env                 # Environment variables
```

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

### Installation
1. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Configure environment variables in `.env` (see `.env.template` for example):
```env
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lexireport
POSTGRES_PORT=5432
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_V1_STR=/api/v1
```
4. Run database migrations:
```bash
alembic upgrade head
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` — Register a new user
- `POST /api/v1/auth/login` — Login and get access token
- `POST /api/v1/auth/password-reset-request` — Request password reset
- `POST /api/v1/auth/password-reset` — Reset password with token

### Users
- `GET /api/v1/users/me` — Get current user info (requires authentication)
- `PUT /api/v1/users/me` — Update current user
- `GET /api/v1/users` — List users (paginated, admin only)
- `GET /api/v1/users/{user_id}` — Get user by ID (admin or self)
- `PUT /api/v1/users/{user_id}` — Update user (admin or self)
- `DELETE /api/v1/users/{user_id}` — Delete user (admin only)
- `PUT /api/v1/users/{user_id}/deactivate` — Deactivate user (admin only)

### Permissions & Roles
- Permissions: `api_access`, `read_users`, `write_users`, `manage_users`
- Roles: `admin` (full access), `user` (limited access)

| Endpoint                  | Required Permission | Role Restriction         |
|---------------------------|--------------------|-------------------------|
| `GET /me`                 | `api_access`       | Any                     |
| `GET /{user_id}`          | `read_users`       | Admin or self           |
| `PUT /me`                 | `api_access`       | Any                     |
| `PUT /{user_id}`          | `write_users`      | Admin or self           |
| `DELETE /{user_id}`       | `manage_users`     | Admin only              |
| `PUT /{user_id}/deactivate`| `manage_users`    | Admin only              |

## Validation Requirements

- **Password:**
  - Minimum 8 characters
  - At least one uppercase, one lowercase, one number, one special character
- **Email:**
  - Valid email format, converted to lowercase
- **Name:**
  - 2-100 characters, only letters, spaces, hyphens, periods, apostrophes
- **Pagination:**
  - Page number > 0, page size 1-100

## Security
- Passwords hashed with bcrypt
- JWT for authentication
- Role-based access control
- Input validation and error handling

## Testing
- Run tests with `pytest` in the backend directory
- See [../docs/testing.md](testing.md) for details

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License. See the LICENSE file for details. 