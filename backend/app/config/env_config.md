# Environment Configuration Guide

## Required Environment Variables

### 1. Database Configuration (PostgreSQL)
```env
# Required - No defaults
POSTGRES_SERVER=localhost        # Database host
POSTGRES_USER=postgres          # Database user
POSTGRES_PASSWORD=your_password  # Database password
POSTGRES_DB=lexireport          # Database name

# Optional - Has defaults
POSTGRES_PORT=5432              # Database port (default: 5432)
```

### 2. Redis Configuration
```env
# Optional - Has defaults
REDIS_HOST=localhost            # Redis host (default: localhost)
REDIS_PORT=6379                # Redis port (default: 6379)
REDIS_DB=0                     # Redis database number (default: 0)
REDIS_PASSWORD=                # Redis password (default: None)
REDIS_SSL=false                # Use SSL (default: false)
REDIS_TIMEOUT=5                # Connection timeout in seconds (default: 5)
REDIS_RETRY_ON_TIMEOUT=true    # Retry on timeout (default: true)
```

### 3. JWT Authentication
```env
# Optional - Has defaults
JWT_SECRET_KEY=                # Secret key for JWT (default: random 32-byte key)
JWT_ALGORITHM=HS256           # JWT algorithm (default: HS256)
ACCESS_TOKEN_EXPIRE_MINUTES=30 # Token expiration in minutes (default: 30)
```

### 4. Database Pool Settings
```env
# Optional - Has defaults
DB_POOL_SIZE=5                # Connection pool size (default: 5)
DB_MAX_OVERFLOW=10            # Maximum overflow connections (default: 10)
DB_POOL_TIMEOUT=30            # Pool timeout in seconds (default: 30)
DB_POOL_RECYCLE=1800          # Connection recycle time in seconds (default: 1800)
```

### 5. CORS Settings
```env
# Optional - Has defaults
BACKEND_CORS_ORIGINS=["http://localhost:3000"]  # Allowed origins (default: ["*"])
```

### 6. Application Settings
```env
# Optional - Has defaults
PROJECT_NAME=LexiReport Backend  # Project name (default: "LexiReport Backend")
VERSION=1.0.0                   # API version (default: "1.0.0")
API_V1_STR=/api/v1             # API prefix (default: "/api/v1")
DESCRIPTION=LexiReport Backend API  # API description
```

## Environment Setup Instructions

1. **Development Environment**
   ```env
   # Database
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=lexireport
   
   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   
   # JWT
   JWT_SECRET_KEY=dev_secret_key
   
   # CORS
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

2. **Production Environment**
   ```env
   # Database
   POSTGRES_SERVER=your_production_db_host
   POSTGRES_USER=your_production_user
   POSTGRES_PASSWORD=your_secure_production_password
   POSTGRES_DB=your_production_db
   
   # Redis
   REDIS_HOST=your_redis_host
   REDIS_PASSWORD=your_redis_password
   REDIS_SSL=true
   
   # JWT
   JWT_SECRET_KEY=your_secure_production_key
   
   # CORS
   BACKEND_CORS_ORIGINS=["https://yourdomain.com"]
   ```

3. **Testing Environment**
   ```env
   # Database
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=lexireport_test
   
   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=1
   
   # JWT
   JWT_SECRET_KEY=test_secret_key
   ```

## Security Best Practices

1. **Database Security**
   - Use strong passwords
   - Restrict database access to application IP
   - Use SSL for database connections in production
   - Regularly rotate database credentials

2. **Redis Security**
   - Set strong Redis passwords
   - Use SSL in production
   - Restrict Redis access to application IP
   - Use separate Redis instances for different environments

3. **JWT Security**
   - Use strong, unique secret keys
   - Regularly rotate JWT secret keys
   - Set appropriate token expiration times
   - Use secure algorithms (HS256 or better)

4. **CORS Security**
   - Restrict CORS origins to specific domains
   - Avoid using wildcard (*) in production
   - Use HTTPS in production
   - Regularly review allowed origins

## Environment Variable Validation

The application validates environment variables using Pydantic:
- Required variables must be provided
- Type checking is enforced
- Default values are used when appropriate
- Values are validated against constraints

## Troubleshooting

1. **Database Connection Issues**
   - Verify database credentials
   - Check database server is running
   - Ensure database exists
   - Check network connectivity

2. **Redis Connection Issues**
   - Verify Redis is running
   - Check Redis credentials
   - Ensure Redis port is accessible
   - Check Redis SSL configuration

3. **JWT Issues**
   - Verify JWT secret key is set
   - Check token expiration time
   - Ensure correct algorithm is used
   - Verify token format

4. **CORS Issues**
   - Check allowed origins
   - Verify frontend URL is included
   - Check SSL configuration
   - Review browser console for errors 