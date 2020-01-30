FROM python:3.6-alpine

# set work directory
WORKDIR /code/cartographer_backend/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY requirements.txt /code/cartographer_backend/
RUN pip install -r requirements.txt

# copy project
COPY . /code/cartographer_backend/

# run entrypoint.sh
ENTRYPOINT ["/code/cartographer_backend/entrypoint.sh"]
