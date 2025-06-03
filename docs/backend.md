# Backend Documentation

## Overview
The backend is built using FastAPI and provides a RESTful API for user authentication and management. It uses PostgreSQL as the database and Alembic for database migrations.

## Project Structure
```
backend/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API routes
│   │   └── auth/        # Authentication endpoints
│   │   └── user/        # User management endpoints
│   │   └── models/      # Database models
│   │   └── main.py      # FastAPI application
│   └── .env             # Environment variables
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

3. Configure environment variables in `.env`:
```env
# PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=lexireport
POSTGRES_PORT=5432

# JWT
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_V1_STR=/api/v1
```

### Database Setup
1. Ensure PostgreSQL is running and accessible
2. Run database migrations:
```bash
cd backend
alembic upgrade head
```

This will:
- Create the database if it doesn't exist
- Create the users table with necessary columns
- Create indexes on email and id columns
- Insert an initial admin user (email: admin@example.com, password: admin123)

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
  - Request body:
    ```json
    {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "John Doe"
    }
    ```

- `POST /api/v1/auth/login` - Login and get access token
  - Request body:
    ```json
    {
        "username": "user@example.com",
        "password": "password123"
    }
    ```
  - Response:
    ```json
    {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "token_type": "bearer"
    }
    ```

### User Management
- `GET /api/v1/users/me` - Get current user information
  - Requires authentication
  - Response:
    ```json
    {
        "id": 1,
        "email": "user@example.com",
        "full_name": "John Doe",
        "created_at": "2024-03-19T10:00:00"
    }
    ```

## User Management API

### Role and Permission Management

#### Update User Permissions
```http
POST /api/v1/users/{user_id}/permissions
Authorization: Bearer <token>
Content-Type: application/json

{
    "permissions": ["read_users", "write_users", "api_access"]
}
```

**Response**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "role": "user",
    "permissions": "read_users,write_users,api_access",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

#### Update User Role
```http
POST /api/v1/users/{user_id}/role
Authorization: Bearer <token>
Content-Type: application/json

{
    "role": "admin"
}
```

**Response**
```json
{
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "role": "admin",
    "permissions": "read_users,write_users,api_access",
    "created_at": "2024-03-20T10:00:00Z",
    "updated_at": "2024-03-20T10:00:00Z"
}
```

### Available Permissions

| Permission | Description |
|------------|-------------|
| `api_access` | Basic API access permission |
| `read_users` | Permission to read user data |
| `write_users` | Permission to update user data |
| `manage_users` | Permission to manage user permissions and roles |

### User Roles

| Role | Description |
|------|-------------|
| `admin` | Has full access to all operations |
| `user` | Regular user with limited access |

### Permission Requirements

| Endpoint | Required Permission | Role Restriction |
|----------|-------------------|------------------|
| `GET /me` | `api_access` | Any |
| `GET /{user_id}` | `read_users` | Admin or own user |
| `PUT /me` | `api_access` | Any |
| `PUT /{user_id}` | `write_users` | Admin or own user |
| `PUT /me/password` | `api_access` | Any |
| `GET /` | `read_users` | Admin sees all, users see only themselves |
| `POST /{user_id}/permissions` | `manage_users` | Admin only |
| `POST /{user_id}/role` | `manage_users` | Admin only |

## Security

### Password Hashing
- Passwords are hashed using bcrypt in the application
- For the initial admin user in migrations, SHA-256 is used

### JWT Authentication
- JWT tokens are used for authentication
- Tokens expire after 30 minutes (configurable)
- Tokens are signed using HS256 algorithm

### CORS
- CORS is enabled for the frontend application
- Allowed origins are configured in the settings

## Development

### Running the Server
```bash
cd backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Database Migrations
- Create a new migration:
```bash
alembic revision --autogenerate -m "description"
```

- Apply migrations:
```bash
alembic upgrade head
```

- Rollback migrations:
```bash
alembic downgrade -1  # Rollback one migration
```

## Testing
```bash
pytest
```

## Deployment
1. Set up a production PostgreSQL database
2. Configure environment variables for production
3. Run migrations
4. Deploy using your preferred method (e.g., Docker, cloud platform)

## Troubleshooting

### Common Issues
1. Database Connection
   - Ensure PostgreSQL is running
   - Check connection settings in `.env`
   - Verify database user permissions

2. Migration Errors
   - Check if database exists
   - Ensure all required tables are dropped before rerunning migrations
   - Verify PostgreSQL version compatibility

3. Authentication Issues
   - Check JWT secret key configuration
   - Verify token expiration settings
   - Ensure correct password hashing

### Logs
- Check application logs for detailed error messages
- Enable debug mode for more verbose logging

## User Model Timestamps

The user model now includes two timestamp fields:
- `created_at`: Automatically set when a user is created
- `updated_at`: Automatically updated whenever a user record is modified

These fields are managed by SQLAlchemy and require a database migration (see below).

### Migration for Timestamps
To add these fields to existing databases:
1. Generate a migration:
   ```bash
   alembic revision --autogenerate -m "add timestamp columns to users table"
   ```
2. If you have existing users, update the migration file to set the current timestamp for all existing rows (see MIGRATIONS.md for details).
3. Apply the migration:
   ```bash
   alembic upgrade head
   ```

After this, all users will have `created_at` and `updated_at` fields, and these will be managed automatically.

# Backend API Documentation

## Authentication

### Register New User
- **POST** `/api/v1/auth/register`
- **Description**: Register a new user with default permissions
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "StrongP@ssw0rd123",
    "full_name": "John Doe"
  }
  ```
- **Password Requirements**:
  - Minimum 8 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one number
  - At least one special character

- **Response**:
  ```json
  {
    "message": "Registration successful",
    "email": "user@example.com",
    "role": "user",
    "permissions": [
      "api_access",
      "read_users",
      "write_users"
    ]
  }
  ```

- **Error Responses**:
  ```json
  // Email already registered
  {
    "detail": "Email already registered"
  }

  // Invalid password format
  {
    "detail": "Password must contain at least 8 characters, one uppercase letter, one lowercase letter, one number, and one special character"
  }

  // Invalid email format
  {
    "detail": "Invalid email format"
  }
  ```

- **Example Usage**:
  ```bash
  # Using curl
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "email": "user@example.com",
      "password": "StrongP@ssw0rd123",
      "full_name": "John Doe"
    }' \
    http://localhost:8000/api/v1/auth/register

  # Using Python requests
  import requests

  response = requests.post(
    "http://localhost:8000/api/v1/auth/register",
    json={
      "email": "user@example.com",
      "password": "StrongP@ssw0rd123",
      "full_name": "John Doe"
    }
  )
  print(response.json())

  # Using JavaScript fetch
  fetch("http://localhost:8000/api/v1/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: "user@example.com",
      password: "StrongP@ssw0rd123",
      full_name: "John Doe"
    })
  })
  .then(response => response.json())
  .then(data => console.log(data));
  ```

### Login
- **POST** `/api/v1/auth/login`
- **Description**: Authenticate user and get access token
- **Request Body**:
  ```json
  {
    "username": "user@example.com",
    "password": "StrongP@ssw0rd123"
  }
  ```
- **Response**:
  ```json
  {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "role": "user",
    "permissions": [
      "api_access",
      "read_users",
      "write_users"
    ]
  }
  ```

- **Error Responses**:
  ```json
  // Invalid credentials
  {
    "detail": "Invalid credentials"
  }

  // Inactive user
  {
    "detail": "Inactive user"
  }
  ```

- **Example Usage**:
  ```bash
  # Using curl
  curl -X POST \
    -H "Content-Type: application/json" \
    -d '{
      "username": "user@example.com",
      "password": "StrongP@ssw0rd123"
    }' \
    http://localhost:8000/api/v1/auth/login

  # Using Python requests
  import requests

  response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    data={
      "username": "user@example.com",
      "password": "StrongP@ssw0rd123"
    }
  )
  print(response.json())

  # Using JavaScript fetch
  fetch("http://localhost:8000/api/v1/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      username: "user@example.com",
      password: "StrongP@ssw0rd123"
    })
  })
  .then(response => response.json())
  .then(data => console.log(data));
  ```

### Using the Access Token
After successful login, include the access token in subsequent requests:

```bash
# Using curl
curl -X GET \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  http://localhost:8000/api/v1/users/me

# Using Python requests
import requests

headers = {
  "Authorization": f"Bearer {access_token}"
}
response = requests.get(
  "http://localhost:8000/api/v1/users/me",
  headers=headers
)
print(response.json())

# Using JavaScript fetch
fetch("http://localhost:8000/api/v1/users/me", {
  headers: {
    "Authorization": `Bearer ${accessToken}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

### Default User Permissions
New users are automatically assigned the following permissions:
- `api_access`: Basic API access
- `read_users`: Can read own user data
- `write_users`: Can update own user data

### Security Notes
1. Always use HTTPS in production
2. Store tokens securely
3. Implement token refresh mechanism
4. Monitor for suspicious activities
5. Implement rate limiting
6. Use strong passwords
7. Keep tokens short-lived

## User Management

### Get Current User
- **GET** `/api/v1/users/me`
- **Auth**: Required
- **Response**: User object with permissions

### Get User by ID
- **GET** `/api/v1/users/{user_id}`
- **Auth**: Required
- **Permissions**: `read_users`
- **Response**: User object with permissions

### Update User
- **PUT** `/api/v1/users/{user_id}`
- **Auth**: Required
- **Permissions**: `write_users` (or own user)
- **Body**: `{ "full_name": string, "email": string }`
- **Response**: Updated user object

## Role and Permission Management

### Get User Permissions
- **GET** `/api/v1/users/{user_id}/permissions`
- **Auth**: Required
- **Permissions**: `read_users` (or own user)
- **Response**: `{ "permissions": string[] }`

### Assign Permission
- **POST** `/api/v1/users/{user_id}/permissions`
- **Auth**: Required
- **Permissions**: `manage_users`
- **Body**: `{ "permission": string }`
- **Response**: `{ "success": boolean }`

### Remove Permission
- **DELETE** `/api/v1/users/{user_id}/permissions/{permission}`
- **Auth**: Required
- **Permissions**: `manage_users`
- **Response**: `{ "success": boolean }`

### Update User Role
- **PUT** `/api/v1/users/{user_id}/role`
- **Auth**: Required
- **Permissions**: `manage_users`
- **Body**: `{ "role": "admin" | "user" }`
- **Response**: Updated user object

## Available Permissions

| Permission | Description |
|------------|-------------|
| `api_access` | Basic API access |
| `read_users` | View user data |
| `write_users` | Modify user data |
| `manage_users` | Manage users and permissions |

## User Roles

| Role | Description |
|------|-------------|
| `admin` | Superuser with full system access |
| `user` | Regular user with limited access |

## Permission Requirements

| Endpoint | Required Permissions | Role Restrictions |
|----------|---------------------|-------------------|
| `/api/v1/users/me` | None | None |
| `/api/v1/users/{id}` | `read_users` | None |
| `/api/v1/users/{id}` (PUT) | `write_users` | None |
| `/api/v1/users/{id}/permissions` | `read_users` | None |
| `/api/v1/users/{id}/permissions` (POST) | `manage_users` | None |
| `/api/v1/users/{id}/permissions/{permission}` (DELETE) | `manage_users` | None |
| `/api/v1/users/{id}/role` | `manage_users` | None |

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 401 | Unauthorized - Missing or invalid token |
| 403 | Forbidden - Missing required permission |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request data |

## Example Usage

### Assign Permission to User
```bash
curl -X POST \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"permission": "read_users"}' \
  http://localhost:8000/api/v1/users/{user_id}/permissions
```

### Update User Role
```bash
curl -X PUT \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"role": "admin"}' \
  http://localhost:8000/api/v1/users/{user_id}/role
``` 