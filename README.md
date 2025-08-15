# Fairy Tales Backend

A FastAPI-based backend application for fairy tale generation and management.

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (copy from .env.example if available)

3. Run the application:
```bash
python run.py
```

## Database Configuration

### Special Characters in Passwords

The application now supports database passwords with special characters (like `@`, `%`, `/`, `?`). These characters are automatically URL-encoded when creating database connection strings.

**Common Issue**: If you encounter "password authentication failed" errors, it might be due to special characters in your password rather than incorrect credentials.

**Testing**: Use the provided test script to verify your database connection:
```bash
python test_db_connection.py
```

### Environment Variables

Required database environment variables:
- `DB_USER`: Database username
- `DB_PASS`: Database password (supports special characters)
- `DB_HOST`: Database host (for local connections)
- `DB_PORT`: Database port (default: 5432)

For Google Cloud SQL:
- `USE_CLOUD_SQL_PROXY`: Set to "true" for Cloud SQL
- `INSTANCE_CONNECTION_NAME`: Your Cloud SQL instance connection name

## Documentation

See the `/docs` folder for detailed documentation on:
- Database structure
- API endpoints
- Common troubleshooting
