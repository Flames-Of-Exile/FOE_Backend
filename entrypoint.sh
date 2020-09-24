#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

flask run --host=0.0.0.0

exec "$@"