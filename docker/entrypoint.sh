#!/bin/bash
# Optional: wait for DB to be ready before starting app

until pg_isready -h $DB_HOST -p $DB_PORT; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

exec "$@"
