# LexiReport Backend

The backend service for LexiReport, built with FastAPI and PostgreSQL.

## Features

- 🔐 JWT Authentication
- 📊 Report Management
- 🤖 AI-powered Analysis
- 📝 API Documentation
- 🔄 Database Migrations
- 🧪 Comprehensive Testing

## API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Get access token
- `POST /api/v1/auth/register` - Register new user
- `GET /api/v1/auth/me` - Get current user

### Reports
- `GET /api/v1/reports/` - List all reports
- `POST /api/v1/reports/` - Upload new report
- `GET /api/v1/reports/{id}` - Get report details
- `GET /api/v1/reports/{id}/insights` - Get report insights

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL
- Virtual environment

### Installation

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize database:
```bash
python -m app.db.init_db
```

5. Run migrations:
```bash
alembic upgrade head
```

### Running the Server

Development:
```bash
uvicorn app.main:app --reload
```

Production:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   └── api.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── db/
│   │   │   ├── init_db.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── report.py
│   │   └── main.py
│   ├── alembic/
│   │   └── versions/
│   ├── tests/
│   ├── .env
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
```

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions

### Testing
```bash
pytest
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Environment Variables

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `CORS_ORIGINS`: Allowed CORS origins

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License. 