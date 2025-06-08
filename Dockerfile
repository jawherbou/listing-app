FROM python:3.11-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y postgresql-client \
 && pip install --upgrade pip \
 && pip install -r requirements.txt
