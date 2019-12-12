#!/bin/bash

if [ ! -f manage.py ]; then
  cd api
fi

./wait-for-it.sh cartographer-db:5432 -- echo "Creating config file"

if [ ! -f cartographer_backend/config.py ]; then
    cp cartographer_backend/config.py.example cartographer_backend/config.py
fi

echo "Apply database migrations"
python manage.py makemigrations && python manage.py migrate

# echo "Create users"
# python manage.py shell -c "from django.contrib.auth.models import User; \
#   User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')"

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
