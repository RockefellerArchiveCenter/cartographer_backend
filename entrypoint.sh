#!/bin/sh

if [ ! -f manage.py ]; then
  cd cartographer_backend
fi

echo "Waiting for postgres..."

while ! nc -z $SQL_HOST $SQL_PORT; do
  sleep 0.1
done

echo "PostgreSQL started"

# apply database migrations
python manage.py migrate

# collect static files
python manage.py collectstatic --no-input --clear

exec "$@"
