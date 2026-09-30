#!/bin/bash
# Start Redis in the background
redis-server --daemonize yes

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start Celery worker in the background
celery -A apps.worker.worker worker --loglevel=info &

# Start the FastAPI web application
exec uvicorn apps.api.app.main:app --host 0.0.0.0 --port 8000
