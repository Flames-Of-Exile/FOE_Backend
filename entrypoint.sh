#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

python manage.py db init
python manage.py db migrate
python manage.py db upgrade
flask run --host=0.0.0.0

exec "$@"