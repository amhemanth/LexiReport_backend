# FastAPI Backend

A modern, secure, and scalable FastAPI backend with user authentication and report management.

## Features

- User authentication with JWT tokens
- Password hashing with bcrypt
- SQLAlchemy ORM with PostgreSQL
- Repository and service layers for business logic
- API versioning
- CORS support
- Environment-based configuration
- Comprehensive error handling
- Type hints and validation with Pydantic
- Enhanced data validation for user inputs
- Secure password, email, and name validation
- Pagination support

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
# Edit .env with your configuration
```
5. Run database migrations:
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
- `POST /api/v1/auth/register` — Register a new user
- `POST /api/v1/auth/login` — Login and get access token
- `POST /api/v1/auth/password-reset-request` — Request password reset
- `POST /api/v1/auth/password-reset` — Reset password with token

### Users
- `GET /api/v1/users/me` — Get current user
- `PUT /api/v1/users/me` — Update current user
- `GET /api/v1/users` — List users (paginated, admin only)
- `GET /api/v1/users/{user_id}` — Get user by ID (admin or self)
- `PUT /api/v1/users/{user_id}` — Update user (admin or self)
- `DELETE /api/v1/users/{user_id}` — Delete user (admin only)
- `PUT /api/v1/users/{user_id}/deactivate` — Deactivate user (admin only)

## Validation Requirements

- **Password:** Minimum 8 characters, at least one uppercase, one lowercase, one number, one special character
- **Email:** Valid email format, converted to lowercase
- **Name:** 2-100 characters, only letters, spaces, hyphens, periods, apostrophes
- **Pagination:** Page number > 0, page size 1-100

## Project Structure

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for detailed documentation of the project structure and architectural decisions.

## Testing

Run tests:
```bash
pytest
```
See [../docs/testing.md](../docs/testing.md) for more details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License. See the LICENSE file for details. 