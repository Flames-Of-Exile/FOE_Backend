#!/bin/sh

echo "Waiting for postgres..."

while ! nc -z db 5432; do
    sleep 0.1
done

echo "PostgreSQL started"

python manage.py db init
python manage.py db migrate
python manage.py db upgrade
python manage.py create_admin
gunicorn --worker-class eventlet -w 1 manage:app --bind 0.0.0.0:5000

exec "$@"