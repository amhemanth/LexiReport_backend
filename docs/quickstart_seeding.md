# Database Seeding Quick Start Guide

This guide provides quick instructions for common database seeding scenarios.

## Quick Commands

### 1. First-Time Setup
```bash
# Initialize database and run migrations
python manage_db.py init

# Seed with default data
python manage_db.py seed
```

### 2. Development Environment
```bash
# Reset and seed (deletes all data)
python manage_db.py reset-and-seed

# Force reseed existing data
python manage_db.py seed --force
```

### 3. Production Environment
```bash
# Create backup before seeding
python manage_db.py backup

# Seed with custom configuration
python manage_db.py seed --config config/production.json
```

### 4. Testing Environment
```bash
# Reset and seed with test data
python manage_db.py reset-and-seed --config config/test.json
```

## Common Scenarios

### Adding New Seed Data
1. Create a new configuration file:
   ```json
   {
       "roles": [...],
       "permissions": [...],
       "users": [...]
   }
   ```
2. Run seeding with the new configuration:
   ```bash
   python manage_db.py seed --config path/to/new_config.json
   ```

### Updating Existing Data
1. Create a configuration file with updated data
2. Use force flag to update:
   ```bash
   python manage_db.py seed --force --config path/to/updated_config.json
   ```

### Troubleshooting
```bash
# Check database health
python manage_db.py health

# View database information
python manage_db.py info

# Run specific migration
python manage_db.py migrate --version <version>
```

## Environment Setup

1. Set required environment variables:
   ```bash
   export POSTGRES_SERVER=localhost
   export POSTGRES_USER=postgres
   export POSTGRES_PASSWORD=your_password
   export POSTGRES_DB=your_database
   ```

2. Or create a `.env` file:
   ```
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_DB=your_database
   ```

## Next Steps

- Read the [full documentation](database_seeding.md) for detailed information
- Check [troubleshooting guide](database_seeding.md#troubleshooting) for common issues
- Review [best practices](database_seeding.md#best-practices) for production use 