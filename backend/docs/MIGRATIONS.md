# Database Migrations Documentation

## Overview
This document describes the database migrations used in the application. Migrations are managed using Alembic and are stored in the `alembic/versions` directory.

## Migration History

### 001 - Initial Migration
**Date**: 2024-03-19
**Description**: Creates the initial database schema with the users table.
**Changes**:
- Creates `users` table with columns:
  - `id` (Integer, Primary Key)
  - `email` (String, Unique, Not Null)
  - `full_name` (String, Not Null)
  - `hashed_password` (String, Not Null)
  - `created_at` (DateTime with timezone, Not Null)
  - `updated_at` (DateTime with timezone, Nullable)
- Creates indexes:
  - `ix_users_email` (Unique index on email)
  - `ix_users_id` (Index on id)
- Inserts initial admin user

### 002 - Add is_active Column
**Date**: 2024-03-19
**Description**: Adds the is_active column to the users table for user account status management.
**Changes**:
- Adds `is_active` column to `users` table:
  - Type: Boolean
  - Not Nullable
  - Default Value: true
  - Purpose: Indicates whether a user account is active or deactivated

### 003 - Add created_at and updated_at Columns to Users
**Date**: 2025-06-03
**Description**: Adds created_at and updated_at columns to the users table for auditing purposes.
**Changes**:
- Adds `created_at` column to `users` table:
  - Type: DateTime
  - Not Nullable
  - Automatically set to current timestamp on insert
- Adds `updated_at` column to `users` table:
  - Type: DateTime
  - Not Nullable
  - Automatically updated to current timestamp on update
- For existing users, both columns are set to the current timestamp during migration.

**Migration Steps**:
- The migration first adds the columns as nullable with a default value of the current timestamp.
- It then updates all existing rows to have the current timestamp.
- Finally, it alters the columns to be NOT NULL and removes the default.

**Upgrade Example**:
```bash
alembic upgrade head
```

## Running Migrations

### Prerequisites
1. Ensure you have activated the virtual environment:
```bash
cd backend
.\venv\Scripts\activate
```

2. Ensure your database connection settings are correct in `.env` file.

### Commands

1. **Create a new migration**:
```bash
alembic revision --autogenerate -m "description of changes"
```

2. **Apply pending migrations**:
```bash
alembic upgrade head
```

3. **Rollback last migration**:
```bash
alembic downgrade -1
```

4. **View migration history**:
```bash
alembic history
```

5. **View current migration version**:
```bash
alembic current
```

## Best Practices

1. **Always create migrations for schema changes**
   - Never modify the database schema directly
   - Use migrations to track all changes

2. **Test migrations**
   - Test both upgrade and downgrade paths
   - Verify data integrity after migrations

3. **Version control**
   - Commit migration files to version control
   - Keep migration history in sync with team

4. **Naming conventions**
   - Use descriptive names for migrations
   - Include ticket/issue numbers if applicable

5. **Documentation**
   - Document significant schema changes
   - Include rationale for complex migrations

## Troubleshooting

### Common Issues

1. **Migration conflicts**
   - Ensure you have the latest migrations
   - Resolve conflicts by creating new migrations

2. **Database connection issues**
   - Verify database credentials
   - Check database server status

3. **Failed migrations**
   - Check migration logs
   - Verify database state
   - Use `alembic downgrade` to rollback if needed

### Getting Help

If you encounter issues with migrations:
1. Check the migration logs
2. Review the Alembic documentation
3. Consult the team's migration history
4. Create an issue if needed 