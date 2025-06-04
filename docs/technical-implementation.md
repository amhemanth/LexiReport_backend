# Technical Implementation Details

## Frontend Implementation

### Authentication System

#### Login Implementation
```typescript
// Key components in login.tsx
const handleLogin = async () => {
  if (!email || !password) {
    Alert.alert('Error', 'Please fill in all fields');
    return;
  }
  setLoading(true);
  try {
    await login(email, password);
    router.replace('/(tabs)');
  } catch (error) {
    Alert.alert('Login Failed', error.message);
  } finally {
    setLoading(false);
  }
};
```
- Uses React's useState for form state management
- Implements loading and error states
- Uses Expo Router for navigation
- Keyboard avoiding for mobile

#### Registration Implementation
```typescript
// Key components in register.tsx
const handleRegister = async () => {
  if (!fullName || !email || !password || !confirmPassword) {
    Alert.alert('Error', 'Please fill in all fields');
    return;
  }
  if (password !== confirmPassword) {
    Alert.alert('Error', 'Passwords do not match');
    return;
  }
  setLoading(true);
  try {
    await register(fullName, email, password);
    router.replace('/(tabs)');
  } catch (error) {
    Alert.alert('Registration Failed', error.message);
  } finally {
    setLoading(false);
  }
};
```
- Password confirmation validation
- API-compatible field naming
- Loading and error states
- Secure password input

### Profile Screen Implementation
```typescript
const ProfileScreen = () => {
  const { logout, user } = useAuth();
  const handleLogout = async () => {
    try {
      await logout();
      router.replace('/(auth)/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };
  // ...
};
```
- Uses custom hooks for auth management
- Secure logout
- Displays user info from auth context

### Theme System
```typescript
export const useTheme = () => {
  const colorScheme = useColorScheme();
  const colors = colorScheme === 'dark' ? darkColors : lightColors;
  return { colors };
};
```
- Consistent color schemes
- Easy access to themed colors

## Backend Implementation

### Project Structure
- FastAPI app in `app/`
- API routes in `app/api/v1/`
- Models in `app/models/`
- Services and repositories for business logic and DB access
- Alembic for migrations

### Database Schema (SQLAlchemy)
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
- SQLAlchemy for schema definition
- Email uniqueness and validation
- Timestamps for tracking

### Authentication System

#### Password Hashing
```python
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password):
    return pwd_context.hash(password)
```
- bcrypt for secure password hashing

#### JWT Implementation
```python
from jose import jwt
from datetime import datetime, timedelta

def create_access_token(data: dict, secret: str, algorithm: str, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret, algorithm=algorithm)
```
- JWT for authentication
- Token expiration and validation

### API Implementation
- Endpoints for registration, login, user management, and report management
- Role-based access control (RBAC) using decorators
- Pydantic for request/response validation

### Error Handling
- Custom exception handlers for validation, authentication, and permissions
- Consistent error responses

### Security
- JWT validation, password hashing
- Input validation
- Role-based access control
- CORS and environment-based configuration

## Database Handling

### Connection Setup
```javascript
// Database connection implementation
mongoose.connect(process.env.MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
})
.then(() => console.log('Connected to MongoDB'))
.catch(err => console.error('MongoDB connection error:', err));
```
- Uses environment variables for configuration
- Implements proper error handling
- Uses modern MongoDB driver options

### Query Optimization
- Implements proper indexing on email field
- Uses lean queries where appropriate
- Implements proper error handling for database operations
- Uses transactions where necessary

### Security Measures
- Implements input validation
- Uses parameterized queries
- Implements proper error handling
- Uses environment variables for sensitive data

## Error Handling

### Frontend Error Handling
```typescript
// API error handling
const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error
    return error.response.data.message;
  } else if (error.request) {
    // No response received
    return 'Network error. Please check your connection.';
  } else {
    // Other errors
    return 'An unexpected error occurred.';
  }
};
```
- Implements proper error categorization
- Provides user-friendly error messages
- Handles network errors
- Implements proper error logging

### Backend Error Handling
```javascript
// Global error handler
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    message: err.message || 'Internal server error',
    error: process.env.NODE_ENV === 'development' ? err : {}
  });
});
```
- Implements global error handling
- Provides proper error logging
- Implements environment-based error details
- Uses proper HTTP status codes 

## Authentication and Authorization

### Role-Based Access Control (RBAC)

The system implements a hybrid RBAC (Role-Based Access Control) system that combines both role-based and permission-based access control:

#### User Roles
- `ADMIN`: Superuser with full system access
- `USER`: Regular user with limited access

#### Permissions
The system uses granular permissions to control access to specific features:

| Permission | Description |
|------------|-------------|
| `api_access` | Basic API access |
| `read_users` | View user data |
| `write_users` | Modify user data |
| `manage_users` | Manage users and permissions |

### Database Structure

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    full_name VARCHAR,
    is_active BOOLEAN DEFAULT true,
    role userrole NOT NULL DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

#### Passwords Table
```sql
CREATE TABLE passwords (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    hashed_password VARCHAR NOT NULL,
    password_updated_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    is_current BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

#### Permissions Table
```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR
);
```

#### User Permissions Table
```sql
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    permission_id UUID REFERENCES permissions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
```

### Permission Checking

The system provides multiple ways to check permissions:

1. **Direct Permission Check**
```python
if user.has_permission("read_users"):
    # Allow access
```

2. **Role-Based Check**
```python
if user.role == UserRole.ADMIN:
    # Allow access
```

3. **API Endpoint Protection**
```python
@router.get("/users")
@require_permissions(["read_users"])
def get_users():
    # Only users with read_users permission can access
```

### Security Implementation

#### Password Security
- Passwords are hashed using bcrypt
- Password history is maintained in the passwords table
- Password updates are tracked with timestamps

#### JWT Token Generation
- Tokens include user ID and role
- Tokens are signed with a secret key
- Tokens expire after a configurable period

#### Permission Management
- Permissions can be assigned/removed by users with `manage_users` permission
- Admin users automatically have all permissions
- Regular users require explicit permission assignment

### User Registration Flow

1. **New User Registration**
   - User submits email and password
   - System creates user record with `USER` role
   - System creates password record with hashed password
   - System assigns default permissions (`api_access`)

2. **Admin User Creation**
   - Created during system initialization
   - Assigned `ADMIN` role
   - Granted all available permissions

### Database Management

The system includes scripts for database management:

1. **Reset Database**
```bash
python manage_db.py reset
```

2. **Seed Initial Data**
```bash
python manage_db.py seed
```

3. **Reset and Seed**
```bash
python manage_db.py reset-and-seed
```

### Best Practices

1. **Permission Checking**
   - Always check permissions at the API level
   - Use decorators for consistent permission checking
   - Implement both role and permission checks where appropriate

2. **Password Management**
   - Never store plain text passwords
   - Maintain password history
   - Enforce password complexity requirements

3. **User Management**
   - Implement proper user deactivation
   - Track user activity
   - Maintain audit logs for permission changes 

## Role and Permission System Implementation

### Design Decisions

1. **Hybrid RBAC System**
   - Combined role-based and permission-based access control
   - Roles provide broad access levels (ADMIN, USER)
   - Permissions provide granular access control
   - Admins automatically have all permissions

2. **Database Structure**
   - Separate tables for users, permissions, and user permissions
   - UUID-based primary keys for better security
   - Timestamps for auditing and tracking
   - Proper foreign key relationships

3. **Default Permissions**
   - New users get basic permissions by default:
     - `api_access`: Basic API access
     - `read_users`: Can read own user data
     - `write_users`: Can update own user data
   - Admin users get all permissions automatically

4. **JWT Token Enhancement**
   - Tokens now include:
     - User email (sub)
     - User role
     - User permissions
   - This allows frontend to make permission-based decisions
   - Reduces need for additional API calls

### Implementation Details

#### User Registration Flow
```python
def register(self, db: Session, user_in: UserCreate) -> dict:
    try:
        # Check for existing user
        if user_repository.get_by_email(db, email=user_in.email):
            raise UserAlreadyExistsError()
        
        # Create user with default role
        user = user_repository.create(
            db=db,
            obj_in=user_in,
            hashed_password=hashed_password,
            role=UserRole.USER,
            is_active=True
        )
        
        # Add default permissions
        default_permissions = [
            PermissionEnum.API_ACCESS.value,
            PermissionEnum.READ_USERS.value,
            PermissionEnum.WRITE_USERS.value
        ]
        
        for permission in default_permissions:
            self._create_user_permission(db, user.id, permission)
        
        db.commit()
        return {"message": "Registration successful", "email": user.email}
    except SQLAlchemyError:
        db.rollback()
        raise DatabaseError()
```

#### Login Flow
```python
def login(self, db: Session, user_in: UserLogin) -> Token:
    try:
        user = user_repository.get_by_email(db, email=user_in.email)
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise InvalidCredentialsError()
        
        if not user.is_active:
            raise InactiveUserError()
        
        # Create token with role and permissions
        access_token = create_access_token(
            data={
                "sub": user.email,
                "role": user.role.value,
                "permissions": user.get_permissions()
            }
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            role=user.role,
            permissions=user.get_permissions()
        )
    except SQLAlchemyError:
        raise DatabaseError()
```

### API Response Structure

#### Registration Response
```json
{
    "message": "Registration successful",
    "email": "user@example.com",
    "role": "user",
    "permissions": ["api_access", "read_users", "write_users"]
}
```

#### Login Response
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "role": "user",
    "permissions": ["api_access", "read_users", "write_users"]
}
```

### Security Considerations

1. **Permission Management**
   - Permissions are stored in a separate table
   - User permissions are managed through a many-to-many relationship
   - Permission changes are tracked with timestamps
   - Admin role bypasses permission checks

2. **Token Security**
   - JWT tokens include role and permissions
   - Tokens are signed with a secret key
   - Tokens have configurable expiration
   - Token data is validated on each request

3. **Database Security**
   - UUIDs for primary keys
   - Proper foreign key constraints
   - Transaction management for atomic operations
   - Error handling with rollback

### Best Practices

1. **Permission Checking**
   - Always check permissions at the API level
   - Use decorators for consistent permission checking
   - Implement both role and permission checks where appropriate
   - Cache permission checks when possible

2. **Error Handling**
   - Use specific exception types
   - Implement proper transaction management
   - Provide clear error messages
   - Log security-related events

3. **Code Organization**
   - Separate concerns (auth, permissions, users)
   - Use dependency injection
   - Implement proper validation
   - Follow REST API best practices

### Future Considerations

1. **Permission Groups**
   - Consider implementing permission groups
   - Allow bulk permission assignment
   - Support hierarchical permissions

2. **Role Customization**
   - Allow custom role creation
   - Support role inheritance
   - Implement role-based permission templates

3. **Audit Logging**
   - Track permission changes
   - Log role modifications
   - Implement audit trails

4. **Performance Optimization**
   - Cache permission checks
   - Optimize database queries
   - Implement permission preloading 

## JWT Security Implementation

### JWT Secret Key

The JWT secret key is a crucial security component in our authentication system. Here's why it's important:

1. **Purpose**
   - Used to sign and verify JWT tokens
   - Ensures tokens haven't been tampered with
   - Prevents unauthorized token creation
   - Validates token authenticity

2. **Implementation**
```python
# In settings.py
JWT_SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
JWT_ALGORITHM = "HS256"  # HMAC with SHA-256

# In security.py
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

3. **Security Best Practices**
   - Never hardcode the secret key in code
   - Use environment variables in production
   - Make the key long and random (at least 32 characters)
   - Rotate the key periodically
   - Keep the key secure and restrict access

4. **Example Configuration**
```env
# .env file
JWT_SECRET_KEY=your-very-long-and-random-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

5. **Token Structure**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user@example.com",
    "role": "user",
    "permissions": ["api_access", "read_users"],
    "exp": 1616239020
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), secret)"
}
```

6. **Verification Process**
```python
def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

7. **Security Considerations**
   - Use HTTPS to prevent token interception
   - Implement token expiration
   - Store tokens securely on the client
   - Implement token refresh mechanism
   - Monitor for token abuse

8. **Common Vulnerabilities to Prevent**
   - Token tampering
   - Token replay attacks
   - Token theft
   - Man-in-the-middle attacks
   - Brute force attacks

9. **Production Deployment Checklist**
   - [ ] Set strong JWT secret key
   - [ ] Use environment variables
   - [ ] Enable HTTPS
   - [ ] Set appropriate token expiration
   - [ ] Implement token refresh
   - [ ] Monitor token usage
   - [ ] Regular security audits
   - [ ] Key rotation policy

10. **Monitoring and Logging**
    - Log failed token verifications
    - Monitor token usage patterns
    - Track token expiration
    - Alert on suspicious activities
    - Maintain audit trails

### Token Lifecycle

1. **Creation**
   - User authenticates (login)
   - System generates token with claims
   - Token is signed with secret key
   - Token is returned to client

2. **Usage**
   - Client includes token in requests
   - Server verifies token signature
   - Server checks token expiration
   - Server validates token claims

3. **Expiration**
   - Token expires after set time
   - Client must refresh or re-authenticate
   - Server rejects expired tokens
   - New token is issued if valid

4. **Refresh**
   - Client requests new token
   - Server validates refresh token
   - New access token is issued
   - Old token is invalidated

### Best Practices for JWT Secret Management

1. **Key Generation**
   ```python
   import secrets
   
   def generate_jwt_secret():
       return secrets.token_hex(32)  # 64 character hex string
   ```

2. **Key Storage**
   ```python
   # settings.py
   from pydantic_settings import BaseSettings
   
   class Settings(BaseSettings):
       JWT_SECRET_KEY: str
       
       class Config:
           env_file = ".env"
   ```

3. **Key Rotation**
   ```python
   def rotate_jwt_secret():
       new_secret = generate_jwt_secret()
       # Update in secure storage
       # Allow grace period for token transition
       # Update environment variable
   ```

4. **Error Handling**
   ```python
   def handle_token_error(error: Exception):
       if isinstance(error, jwt.ExpiredSignatureError):
           return {"error": "Token has expired"}
       elif isinstance(error, jwt.InvalidTokenError):
           return {"error": "Invalid token"}
       else:
           return {"error": "Authentication failed"}
   ``` 