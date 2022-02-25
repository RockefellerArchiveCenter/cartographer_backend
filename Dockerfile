FROM python:3.10-buster

# set environment variables
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get install -y \
      postgresql \
    && rm -rf /var/lib/apt/lists/*

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
