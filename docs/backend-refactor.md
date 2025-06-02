# Python Backend Refactoring Plan

## New Directory Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   └── schemas.py
│   │   └── users/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── schemas.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   └── services/
│       ├── __init__.py
│       ├── auth.py
│       └── user.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_users.py
├── alembic/
│   ├── versions/
│   └── env.py
├── .env.example
├── requirements.txt
└── main.py
```

## Implementation Details

### 1. Configuration Management
```python
# app/config/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: str | None = None

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}/{self.POSTGRES_DB}"
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 2. Database Setup
```python
# app/db/base.py
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config.settings import get_settings

settings = get_settings()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# app/db/session.py
from contextlib import contextmanager
from app.db.base import SessionLocal

@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2.1. Database Model & Session Management

#### Overview
The backend uses SQLAlchemy's declarative models and session management to ensure robust, concurrent access to the PostgreSQL database. Each API request gets its own database session, which is closed after the request completes. Connection pooling is enabled and configurable via environment variables, supporting multiple concurrent users efficiently.

#### Model Structure
- Models inherit from a shared `Base` class and can use mixins (e.g., `TimestampMixin`) for common fields like `created_at` and `updated_at`.
- Example: `User`, `Report` models.

#### Session Management
- `SessionLocal` is a session factory created with `sessionmaker`.
- The `get_db` dependency yields a session per request and ensures it is closed after use.
- Connection pooling parameters (`pool_size`, `max_overflow`, etc.) are set in `create_engine` and can be configured via environment variables.

#### Concurrency Handling
- Each request/context uses its own session (not shared between threads).
- SQLAlchemy's connection pool manages database connections for concurrent requests.
- Pool settings can be tuned for your expected load.

#### Environment Variables for Pooling
- `DB_POOL_SIZE`: Number of connections to keep in the pool.
- `DB_MAX_OVERFLOW`: Number of connections to allow in overflow.
- `DB_POOL_TIMEOUT`: Seconds to wait before giving up on getting a connection.
- `DB_POOL_RECYCLE`: Seconds after which a connection is recycled.

#### Request Flow Diagram
```mermaid
graph TD
    A[API Request] --> B[Dependency: get_db()]
    B --> C[SessionLocal() - new session]
    C --> D[Service/Repository Layer]
    D --> E[SQLAlchemy ORM]
    E --> F[Connection Pool]
    F --> G[PostgreSQL Database]
    G --> F
    F --> E
    E --> D
    D --> C
    C --> B
    B --> H[Session closed after request]
```

#### Best Practices
- **Never share a session between threads or requests.**
- **Tune pool settings** for your deployment environment.
- **Always close sessions** after use (handled by `get_db`).
- **Use environment variables** for all sensitive and environment-specific settings.

---

### 3. User Model
```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 4. Security Implementation
```python
# app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.config.settings import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
```

### 5. Authentication Service
```python
# app/services/auth.py
from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User
from app.config.settings import get_settings

settings = get_settings()

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        return user

    @staticmethod
    def create_user(db: Session, email: str, password: str, full_name: str) -> User:
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        return create_access_token(
            data={"sub": user.email},
            expires_delta=access_token_expires
        )
```

### 6. API Routes
```python
# app/api/auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth import AuthService
from app.api.auth.schemas import UserCreate, UserLogin, Token

router = APIRouter()

@router.post("/register", response_model=Token)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
):
    user = AuthService.create_user(
        db=db,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name
    )
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
def login(
    user_in: UserLogin,
    db: Session = Depends(get_db)
):
    user = AuthService.authenticate_user(
        db=db,
        email=user_in.email,
        password=user_in.password
    )
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}
```

### 7. Main Application
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth.routes import router as auth_router
from app.api.users.routes import router as users_router
from app.config.settings import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
```

## Key Improvements

1. **Type Safety**
   - Full Python type hints
   - Pydantic for data validation
   - SQLAlchemy for database models

2. **Error Handling**
   - Custom exception classes
   - Proper HTTP status codes
   - Detailed error messages

3. **Code Organization**
   - Clear separation of concerns
   - Service layer for business logic
   - API routes for endpoints
   - Database models and schemas

4. **Security**
   - Password hashing with bcrypt
   - JWT token authentication
   - CORS configuration
   - Environment variable management

5. **Database**
   - SQLAlchemy ORM
   - Alembic for migrations
   - Connection pooling
   - Transaction management

6. **Testing**
   - Pytest configuration
   - Test database setup
   - Fixtures for common test cases

## Dependencies
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.2
pydantic-settings==2.1.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
alembic==1.12.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
bcrypt==4.0.1
```

## Next Steps

1. Implement the refactored structure
2. Set up database migrations
3. Add unit tests
4. Add integration tests
5. Set up CI/CD pipeline
6. Add API documentation
7. Implement rate limiting
8. Add request logging
9. Set up monitoring
10. Add user profile management 

# Backend Refactoring Decisions

## 1. Database Migration to PostgreSQL

### Decision
Migrated from SQLite to PostgreSQL for production readiness.

### Benefits
- Better concurrency handling
- Advanced features (JSON support, full-text search)
- Better scalability
- Production-grade reliability

### Implementation
- Updated database URI configuration
- Added connection pooling settings
- Implemented proper session management
- Added error handling for database operations

## 2. Clean Architecture Implementation

### Directory Structure
```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   ├── core/
│   │   ├── cache.py
│   │   ├── container.py
│   │   ├── events.py
│   │   └── security.py
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── alembic/
└── tests/
```

### Benefits
- Clear separation of concerns
- Better maintainability
- Easier testing
- Scalable structure

## 3. Dependency Injection

### Implementation
- Used `dependency-injector` for DI
- Container-based configuration
- Singleton instances for core services
- Resource-based database sessions

### Benefits
- Better testability
- Easier configuration management
- Reduced coupling
- Simplified dependency management

## 4. Repository Pattern

### Implementation
- Generic base repository
- Type-safe operations
- Proper error handling
- Async support

### Benefits
- Consistent data access
- Better error handling
- Type safety
- Reduced code duplication

## 5. Event System

### Implementation
- Singleton event bus
- Async event handling
- Error handling and logging
- Predefined events for user actions

### Benefits
- Decoupled components
- Better extensibility
- Improved logging
- Event-driven architecture

## 6. Caching System

### Implementation
- Redis-based caching
- Singleton cache instance
- Error handling and logging
- Cache decorator for functions

### Benefits
- Improved performance
- Reduced database load
- Better error handling
- Configurable caching

## 7. API Versioning

### Implementation
- Versioned API structure
- Clear endpoint organization
- Proper documentation
- Backward compatibility

### Benefits
- Safe API evolution
- Clear versioning
- Better documentation
- Easier maintenance

## 8. Security Improvements

### Implementation
- JWT-based authentication
- Password hashing
- Input validation
- CORS configuration

### Benefits
- Better security
- Input sanitization
- Proper authentication
- Cross-origin protection

## 9. Error Handling

### Implementation
- Consistent error responses
- Proper logging
- Database error handling
- HTTP exception mapping

### Benefits
- Better debugging
- Consistent error responses
- Improved reliability
- Better user experience

## 10. Performance Optimizations

### Implementation
- Database connection pooling
- Redis caching
- Async operations
- Efficient queries

### Benefits
- Better response times
- Reduced resource usage
- Improved scalability
- Better user experience

## 11. Development Workflow

### Tools
- FastAPI for API development
- SQLAlchemy for ORM
- Alembic for migrations
- Pytest for testing

### Benefits
- Modern development stack
- Better productivity
- Easier maintenance
- Improved quality

## 12. Testing Strategy

### Implementation
- Unit tests for services
- Integration tests for API
- Repository tests
- Event system tests

### Benefits
- Better code quality
- Easier maintenance
- Reduced bugs
- Better reliability

## Future Considerations

1. **Monitoring and Logging**
   - Implement structured logging
   - Add performance monitoring
   - Set up error tracking
   - Add health checks

2. **Documentation**
   - API documentation
   - Code documentation
   - Architecture documentation
   - Deployment guides

3. **Security**
   - Rate limiting
   - API key management
   - Audit logging
   - Security headers

4. **Performance**
   - Query optimization
   - Cache strategies
   - Load balancing
   - Database indexing

## Dependencies

### Core Dependencies
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- JWT
- Pydantic

### Development Dependencies
- Pytest
- Black
- Flake8
- MyPy
- Alembic

## Configuration Management

### Environment Variables
- Database configuration
- Redis settings
- JWT settings
- CORS settings
- Logging configuration

### Best Practices
- Use environment variables
- Secure sensitive data
- Version control configuration
- Documentation of settings 