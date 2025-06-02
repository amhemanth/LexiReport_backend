# FastAPI Backend

A modern, secure, and scalable FastAPI backend with user authentication.

## Features

- User authentication with JWT tokens
- Password hashing with bcrypt
- SQLAlchemy ORM with PostgreSQL
- Repository pattern for database operations
- Service layer for business logic
- API versioning
- CORS support
- Environment-based configuration
- Comprehensive error handling
- Type hints and validation with Pydantic
- Enhanced data validation for user inputs
- Secure password requirements
- Email format validation
- Name format validation
- Pagination validation

## Prerequisites

- Python 3.8+
- PostgreSQL
- pip (Python package manager)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.template .env
```

5. Update the `.env` file with your configuration:
```env
# API settings
PROJECT_NAME=FastAPI Backend
VERSION=0.1.0
DESCRIPTION=FastAPI backend with user authentication

# CORS settings
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8000"]

# JWT settings
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database settings
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app
```

6. Create the database:
```bash
createdb app
```

7. Run migrations:
```bash
alembic upgrade head
```

## Development

1. Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

2. Access the API documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register a new user
  - Requires valid email format
  - Password must meet strength requirements
  - Full name must be properly formatted
- `POST /api/v1/auth/login` - Login and get access token
- `POST /api/v1/auth/password-reset-request` - Request password reset
- `POST /api/v1/auth/password-reset` - Reset password with token

### Users
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users` - List users (paginated)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user

## Validation Requirements

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Email Requirements
- Valid email format
- Automatically converted to lowercase

### Name Requirements
- 2-100 characters
- Only letters, spaces, hyphens, periods, and apostrophes
- Cannot be empty

### Pagination Requirements
- Page number must be greater than 0
- Page size must be between 1 and 100

## Project Structure

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed documentation of the project structure and architectural decisions.

## Testing

Run tests:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 