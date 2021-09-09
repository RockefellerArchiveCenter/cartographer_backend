FROM python:3.7

# set environment variables
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get install -y \
      postgresql \
      netcat \
      apache2 \
      apache2-dev \
      libapache2-mod-wsgi-py3 \
    && rm -rf /var/lib/apt/lists/*

RUN a2dissite 000-default

# Copy Apache configs
COPY apache/django.conf /etc/apache2/sites-available/cartographer.conf
RUN a2ensite cartographer.conf

WORKDIR /code/cartographer_backend/

# install dependencies
COPY requirements.txt /code/cartographer_backend/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /code/cartographer_backend/

EXPOSE 8000

# run entrypoint.sh
ENTRYPOINT ["/code/cartographer_backend/entrypoint.sh"]
