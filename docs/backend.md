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