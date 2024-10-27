#!/bin/sh

Docker/migrate.sh

echo "Starting FastAPI server..."

gunicorn src.app:app --bind 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker
