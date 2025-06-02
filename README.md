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

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
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