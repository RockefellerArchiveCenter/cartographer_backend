FROM python:3.6

ENV PYTHONUNBUFFERED 1
WORKDIR /code/cartographer_backend/
ADD requirements.txt /code/cartographer_backend/
RUN pip install --upgrade pip && pip install -r requirements.txt
ADD . /code/cartographer_backend/
RUN ls
