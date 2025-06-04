# Features Documentation

## Frontend Features

### Authentication
- **Login & Registration**
  - Email and password authentication
  - Password strength validation
  - Show/hide password toggle
  - Loading and error states
  - Keyboard avoiding for mobile
  - Modern UI with icons

### Report Management
- **Report List & Detail**
  - List, search, filter, and sort reports
  - Pull-to-refresh and infinite scroll
  - Report metadata and document preview
  - AI-generated insights
  - Share and download options

- **Report Upload**
  - File type and size validation
  - Upload progress and feedback

### Profile & Account
- **User Info**
  - Avatar, name, email display
  - Edit profile (UI ready)
  - Change password (UI ready)
  - Logout and support options

### UI/UX
- **Theme Support**
  - Dark/Light mode
- **Navigation**
  - Tab and stack navigation
- **Form Handling**
  - Input validation, error messages, keyboard handling

## Backend Features

### Authentication & User Management
- **User Registration & Login**
  - Email validation, password hashing (bcrypt)
  - JWT token generation and validation
- **Profile Management**
  - Get/update profile, change password
  - Role and permission management (RBAC)

### Report Management
- **Storage & Processing**
  - Secure file upload, type/size validation
  - Document parsing, text extraction, metadata
  - AI-powered analysis and insights
- **Retrieval**
  - List/search/filter/sort reports (pagination)

### AI Integration
- **Document Analysis**
  - Text extraction, key insights, summaries
  - Entity recognition, sentiment analysis

### Security
- JWT validation, password hashing
- Input validation, error handling
- Role-based access control

## Pending Features
- Edit Profile (backend)
- Change Password (backend)
- Settings management
- Help & Support system
- Email verification
- Password reset
- Social authentication
- Profile picture upload
- User preferences
- Activity logging

## Technical Stack
- **Frontend:** React Native, Expo, Zustand, Expo Router, Axios
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, JWT, Alembic

## Security Measures
- Password hashing (bcrypt)
- JWT authentication
- Protected routes
- Input validation
- Secure storage of sensitive data

## User Management

### Role-Based Access Control (RBAC)
- Permissions: `api_access`, `read_users`, `write_users`, `manage_users`
- Roles: `admin` (full access), `user` (limited access)

### API Access Control

1. **Protected Routes**
   - All routes require authentication
   - Permission-based access control
   - Role-based restrictions
   - Clear error messages for unauthorized access

2. **Permission Management**
   - Admin can update user permissions
   - Permission inheritance for admin role
   - Granular permission control
   - Permission validation

3. **User Data Access**
   - Users can only access their own data
   - Admins can access all user data
   - Permission-based data access
   - Clear access restrictions

## Authentication

### User Registration
- Email and password-based registration
- Password strength requirements
- Email validation
- Duplicate email prevention

### User Login
- JWT-based authentication
- Token expiration
- Secure password verification
- Session management

### Password Management
- Secure password hashing
- Password update functionality
- Password strength validation
- Password update tracking

## Security

### Data Protection
- Encrypted password storage
- Secure token generation
- Role-based access control
- Permission-based restrictions

### API Security
- JWT authentication
- Token validation
- Permission checking
- Role verification

### Error Handling
- Clear error messages
- Proper HTTP status codes
- Security-focused error responses
- Detailed validation errors 