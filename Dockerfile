# See https://hub.docker.com/r/library/python/ for all supported Python
# tags from Docker Hub.
# FROM tiangolo/uwsgi-nginx:python3.6-alpine3.7
FROM tiangolo/uwsgi-nginx:python3.6-alpine3.7
#FROM debian:stretch-slim


# If you prefer miniconda:
#FROM continuumio/miniconda3

LABEL Name=code6 Version=0.0.1
EXPOSE 8000
ENV LISTEN_PORT=8000

# Indicate where uwsgi.ini lives
ENV UWSGI_INI uwsgi.ini

WORKDIR /app
ADD . /app

RUN chmod g+w /app
RUN chmod g+w /app/db.sqlite3

# Using pip to install all required packages:
RUN python3 -m pip install -r requirements.txt


