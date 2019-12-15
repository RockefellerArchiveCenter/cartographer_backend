#!/bin/sh

if [ ! -f manage.py ]; then
  cd cartographer_backend
fi

./wait-for-it.sh cartographer-db:5432 -- echo "Running entrypoint.sh"

# apply database migrations
python manage.py migrate

# collect static files
python manage.py collectstatic --no-input --clear

exec "$@"
