#!/bin/bash

# Create config.py if it doesn't exist
if [ ! -f cartographer_backend/config.py ]; then
    echo "Creating config file"
    cp cartographer_backend/config.py.example cartographer_backend/config.py
fi

./wait-for-it.sh db:5432 -- echo "Apply database migrations"
python manage.py migrate

#Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
