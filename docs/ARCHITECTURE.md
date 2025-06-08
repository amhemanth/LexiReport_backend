# LexiReport Architecture

## System Overview

```mermaid
graph TD
    A[Mobile/Web Frontend (Expo/React Native)] -->|REST API| B[API Gateway (FastAPI)]
    B -->|Business Logic| C[Backend Services]
    C -->|AI Calls| D[AI Services]
    C -->|DB Access| E[PostgreSQL Database]
    C -->|File Ops| F[Object/File Storage]
    C -->|Notifications| G[Notification Service]
    D -->|Model Inference| H[AI Models]
    D -->|Cache| I[Redis]
```

## Feature Coverage

```mermaid
graph LR
    subgraph Frontend
      FE1[Authentication] --> FE2[Report Management]
      FE2 --> FE3[AI Insights]
      FE3 --> FE4[Voice/Audio]
      FE4 --> FE5[BI Integration]
      FE5 --> FE6[Q&A]
      FE6 --> FE7[Offline Mode]
      FE7 --> FE8[Notifications]
      FE8 --> FE9[User Preferences]
      FE9 --> FE10[Collaboration]
    end
    subgraph Backend
      BE1[Auth API] --> BE2[Report API]
      BE2 --> BE3[AI API]
      BE3 --> BE4[BI API]
      BE4 --> BE5[Notification API]
      BE5 --> BE6[Collaboration API]
    end
    FE1 -.-> BE1
    FE2 -.-> BE2
    FE3 -.-> BE3
    FE4 -.-> BE3
    FE5 -.-> BE4
    FE6 -.-> BE3
    FE7 -.-> BE2
    FE8 -.-> BE5
    FE9 -.-> BE1
    FE10 -.-> BE6
```

- **Solid lines**: Implemented
- **Dashed lines**: In progress or planned

## Folder Structure (2024)

### Frontend
```
frontend/
├── app/           # Expo Router app directory
│   ├── (auth)/    # Authentication screens
│   ├── (tabs)/    # Main app tabs (profile, reports, upload, etc.)
│   └── _layout.tsx
├── components/    # Reusable components (Header, PermissionGate, etc.)
├── hooks/         # Custom React hooks
├── services/      # API and business logic
├── store/         # Zustand state management
├── models/        # TypeScript models/types
├── utils/         # Helper functions
├── config/        # App configuration
├── constants/     # Static values (permissions, colors)
└── assets/        # Images and static assets
```

### Backend
```
backend/
├── app/
│   ├── api/         # API endpoints (v1)
│   ├── core/        # Core logic (security, exceptions)
│   ├── models/      # SQLAlchemy models
│   ├── schemas/     # Pydantic schemas
│   ├── services/    # Business logic
│   └── utils/       # Helper functions
├── tests/           # Test files
└── alembic/         # Database migrations
```

## Permissions & Roles (RBAC)

```mermaid
graph TD
    Admin[Admin]
    User[User]
    Guest[Guest]
    Admin -->|manage_users| API
    Admin -->|read_users| API
    Admin -->|write_users| API
    User -->|api_access| API
    User -->|read_own| API
    Guest -->|register| API
```

- **Admin**: Full access (manage users, all reports, settings)
- **User**: Access to own reports, profile, AI features
- **Guest**: Registration, limited access

## Achievements (2024)

- ✅ Modern, cross-platform frontend (Expo/React Native)
- ✅ Secure authentication (JWT, RBAC)
- ✅ Report upload, management, and AI-powered insights
- ✅ Voice-over, Q&A, and BI integration (MVP)
- ✅ Offline mode, notifications, and user preferences
- ✅ Collaboration (sharing, comments, tags)
- ✅ Robust backend (FastAPI, PostgreSQL, Alembic)
- ✅ Modular AI services (summarization, TTS, Q&A)
- ✅ CI/CD, monitoring, and scalable deployment

---

*See API_REFERENCE.md for endpoint details and AI_IMPLEMENTATION_PLAN.md for AI pipeline.*

## 1. Development Architecture

### 1.1 Frontend Architecture
```
frontend/
├── app/                    # Expo Router app directory
│   ├── (auth)/            # Authentication screens
│   ├── (tabs)/            # Main app tabs
│   └── _layout.tsx        # Root layout
├── components/            # Reusable components
│   ├── common/           # Shared components
│   ├── reports/          # Report-specific components
│   └── voice/            # Voice interaction components
├── hooks/                # Custom React hooks
├── services/            # API and external services
├── store/              # Zustand state management
├── utils/              # Helper functions
└── config/             # Configuration files
```

### 1.2 Backend Architecture
```
backend/
├── app/
│   ├── api/            # API endpoints
│   │   └── v1/        # API version 1
│   ├── core/          # Core functionality
│   ├── models/        # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── utils/         # Helper functions
├── tests/             # Test files
└── alembic/           # Database migrations
```

### 1.3 AI Services Architecture
```
backend/
└── app/
    └── services/
        └── ai/
            ├── text_extraction/    # Document processing
            ├── summarization/      # Text summarization
            ├── tts/               # Text-to-speech
            ├── voice_commands/    # Voice recognition
            └── analysis/          # Report analysis
```

## 2. Component Interactions

### 2.1 Frontend to Backend
```mermaid
sequenceDiagram
    participant F as Frontend
    participant A as API Gateway
    participant B as Backend
    participant D as Database
    
    F->>A: HTTP Request
    A->>B: Route Request
    B->>D: Query Data
    D-->>B: Return Data
    B-->>A: Process Response
    A-->>F: HTTP Response
```

### 2.2 AI Processing Flow
```mermaid
sequenceDiagram
    participant F as Frontend
    participant B as Backend
    participant AI as AI Services
    participant S as Storage
    
    F->>B: Upload Document
    B->>S: Store Document
    B->>AI: Process Document
    AI->>AI: Extract Text
    AI->>AI: Generate Summary
    AI->>AI: Create Voice-over
    AI-->>B: Return Results
    B-->>F: Update UI
```

## 3. Development Environment

### 3.1 Local Development
```yaml
Development Stack:
  Frontend:
    - Node.js 16+
    - Expo CLI
    - React Native
    - TypeScript
  
  Backend:
    - Python 3.8+
    - FastAPI
    - PostgreSQL
    - Redis (Caching)
  
  AI Services:
    - PyTorch
    - Transformers
    - TTS
    - Whisper
```

### 3.2 Development Workflow
1. **Version Control**
   - Git for source control
   - Feature branch workflow
   - Pull request reviews

2. **Testing**
   - Unit tests (Jest, Pytest)
   - Integration tests
   - E2E tests (Detox)

3. **Code Quality**
   - ESLint/Prettier
   - Black/Pylint
   - Type checking
   - CI/CD pipelines

## 4. Deployment Architecture

### 4.1 Production Environment
```mermaid
graph TD
    A[CDN] --> B[Load Balancer]
    B --> C[API Servers]
    C --> D[Database Cluster]
    C --> E[Redis Cache]
    C --> F[Object Storage]
    C --> G[AI Services]
    G --> H[GPU Servers]
```

### 4.2 Infrastructure Components

#### 4.2.1 Frontend Deployment
- **Hosting**: Vercel/Netlify
- **CDN**: Cloudflare
- **Mobile**: App Store/Play Store
- **Web**: Progressive Web App

#### 4.2.2 Backend Deployment
- **API Servers**: Kubernetes
- **Database**: Managed PostgreSQL
- **Cache**: Redis Cluster
- **Storage**: S3/Cloud Storage
- **AI Services**: GPU-enabled instances

### 4.3 Scaling Strategy

#### 4.3.1 Horizontal Scaling
- Stateless API servers
- Read replicas for database
- Multiple AI service instances

#### 4.3.2 Vertical Scaling
- GPU optimization for AI
- Database optimization
- Cache optimization

## 5. Security Architecture

### 5.1 Authentication Flow
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant D as Database
    
    U->>F: Login Request
    F->>B: Authenticate
    B->>D: Verify Credentials
    D-->>B: User Data
    B-->>F: JWT Token
    F-->>U: Store Token
```

### 5.2 Security Measures
- JWT authentication
- HTTPS encryption
- Rate limiting
- Input validation
- CORS policies
- Security headers

## 6. Monitoring and Logging

### 6.1 Monitoring Stack
- Prometheus for metrics
- Grafana for visualization
- ELK stack for logging
- Sentry for error tracking

### 6.2 Key Metrics
- API response times
- Error rates
- Resource usage
- AI processing times
- User engagement

## 7. Disaster Recovery

### 7.1 Backup Strategy
- Database backups
- File storage backups
- Configuration backups
- Regular testing

### 7.2 Recovery Procedures
- Database restoration
- Service failover
- Data recovery
- Incident response

## 8. Performance Optimization

### 8.1 Frontend
- Code splitting
- Lazy loading
- Image optimization
- Cache strategies

### 8.2 Backend
- Query optimization
- Connection pooling
- Caching layers
- Async processing

### 8.3 AI Services
- Model optimization
- Batch processing
- GPU utilization
- Result caching

## 9. Development Guidelines

### 9.1 Code Organization
- Feature-based structure
- Clear separation of concerns
- Consistent naming conventions
- Documentation requirements

### 9.2 Testing Requirements
- Unit test coverage
- Integration test scenarios
- Performance benchmarks
- Security testing

### 9.3 Documentation
- API documentation
- Component documentation
- Setup guides
- Deployment procedures 