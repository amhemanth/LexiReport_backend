# Database Seeding Documentation

This document provides comprehensive information about database seeding in the application, including how to run, manage, and customize the seeding process.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Basic Usage](#basic-usage)
- [Advanced Usage](#advanced-usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The database seeding system provides a robust way to populate the database with initial data. It supports:
- Basic seeding of essential data
- Custom seeding through configuration files
- Force reseeding of existing data
- Proper error handling and transaction management
- Data validation before insertion

## Prerequisites

Before running the seeding process, ensure you have:

1. Python 3.8+ installed
2. All required dependencies installed:
   ```bash
   pip install -r requirements.txt
   ```
3. Database connection properly configured in your environment
4. Sufficient permissions to modify the database

## Basic Usage

### Simple Seeding

To seed the database with default data:

```bash
python manage_db.py seed
```

This will:
- Create default roles and permissions
- Create initial users
- Set up basic system configurations
- Create sample data for testing

### Force Reseeding

To force reseed the database (will delete existing data):

```bash
python manage_db.py seed --force
```

### Reset and Seed

To completely reset the database and seed it:

```bash
python manage_db.py reset-and-seed
```

## Advanced Usage

### Custom Configuration

You can customize the seed data using a JSON configuration file:

```bash
python manage_db.py seed --config path/to/config.json
```

Example configuration file (`config.json`):
```json
{
    "roles": [
        {
            "name": "custom_role",
            "description": "Custom role description"
        }
    ],
    "permissions": [
        {
            "name": "custom:permission",
            "description": "Custom permission description"
        }
    ],
    "users": [
        {
            "email": "custom@example.com",
            "username": "custom_user",
            "password": "custom_password"
        }
    ]
}
```

### Database Management Commands

The system provides several database management commands:

```bash
# Initialize database
python manage_db.py init

# Reset database
python manage_db.py reset

# Run migrations
python manage_db.py migrate

# Check database health
python manage_db.py health

# Create database backup
python manage_db.py backup
```

## Configuration

### Command Line Options

- `--force`: Force reseeding even if data exists
- `--confirm`: Skip confirmation prompts
- `--config`: Path to seed configuration file
- `--version`: Specific migration version to use

### Environment Variables

The following environment variables can be configured:

```bash
# Database connection
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_database
POSTGRES_PORT=5432

# Seeding options
SEED_FORCE=false
SEED_CONFIG_PATH=path/to/config.json
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check database credentials
   - Ensure database server is running
   - Verify network connectivity

2. **Permission Errors**
   - Ensure user has sufficient database permissions
   - Check file permissions for configuration files

3. **Data Validation Errors**
   - Verify configuration file format
   - Check required fields in seed data
   - Ensure data types match schema

### Error Messages

Common error messages and their solutions:

```
Error: Database already contains data
Solution: Use --force flag to reseed

Error: Invalid configuration file
Solution: Check JSON format and required fields

Error: Database connection failed
Solution: Verify database credentials and connection
```

## Best Practices

1. **Development Environment**
   - Use `--force` flag during development
   - Keep configuration files in version control
   - Document custom seed data

2. **Production Environment**
   - Never use `--force` in production without backup
   - Use configuration files for environment-specific data
   - Test seeding process in staging first

3. **Data Management**
   - Keep sensitive data out of configuration files
   - Use environment variables for sensitive information
   - Regularly backup database before seeding

4. **Performance**
   - Use bulk inserts for large datasets
   - Consider using transactions for atomic operations
   - Monitor database performance during seeding

## Additional Resources

- [Database Schema Documentation](database_schema.md)
- [API Documentation](api_documentation.md)
- [Environment Setup Guide](environment_setup.md) 