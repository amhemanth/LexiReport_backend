# LexiReport

LexiReport is an AI-powered document analysis application that helps users analyze and extract insights from their reports.

## Features

- 📱 Modern mobile-first design
- 🌓 Dark mode support
- 🔐 Secure authentication
- 📊 Report analysis and insights
- 📤 Easy report upload
- 📱 Cross-platform support (iOS, Android, Web)

## Tech Stack

### Frontend
- React Native
- Expo
- TypeScript
- Zustand (State Management)
- React Navigation
- Axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Python 3.9+

## Getting Started

### Prerequisites
- Node.js 16+
- Python 3.9+
- PostgreSQL
- Expo CLI

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lexireport.git
cd lexireport
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m app.db.init_db
uvicorn app.main:app --reload
```

3. Set up the frontend:
```bash
cd frontend
npm install
npx expo start
```

## Project Structure

```
lexireport/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   └── main.py
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── app/
│   │   ├── (app)/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   ├── assets/
│   └── README.md
└── README.md
```

## Development

### Backend Development
- API documentation available at `/docs` when running the server
- Database migrations handled through Alembic
- Environment variables in `.env` file

### Frontend Development
- Expo development server
- Hot reloading enabled
- TypeScript for type safety
- Component-based architecture

## Testing

For detailed information about running tests, test configuration, and best practices, please refer to the [Testing Documentation](docs/testing.md).

Quick start:
```bash
# Navigate to backend directory
cd backend

# Run all tests
pytest

# Run tests with coverage
pytest --cov=app tests/
```

## Deployment

### Backend Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Run migrations
4. Deploy with uvicorn/gunicorn

### Frontend Deployment
1. Build with Expo
2. Deploy to app stores
3. Configure environment variables

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@lexireport.com or open an issue in the repository.

## Project Structure
```
.
├── backend/             # FastAPI backend
├── frontend/           # React frontend
└── docs/              # Documentation
```

## Backend Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Virtual environment (recommended)

### Installation
1. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the backend directory with the following content:
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

4. Set up the database:
```bash
cd backend
alembic upgrade head
```

### Running the Backend Server

#### Windows
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Linux/Mac
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- Local: `http://localhost:8000`
- Network: `http://<your-ip-address>:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Frontend Setup

### Prerequisites
- Node.js 16+
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Running the Frontend Development Server
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Development

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Testing
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

### Backend
1. Set up a production PostgreSQL database
2. Configure environment variables for production
3. Run migrations
4. Deploy using your preferred method (e.g., Docker, cloud platform)

### Frontend
1. Build the frontend:
```bash
cd frontend
npm run build
```
2. Deploy the built files to your web server

## Documentation
Detailed documentation is available in the `docs` directory:
- [Backend Documentation](docs/backend.md)
- [Frontend Documentation](docs/frontend.md)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 