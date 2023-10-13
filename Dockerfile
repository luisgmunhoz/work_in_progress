FROM python:3.8
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
RUN apt-get update && apt-get upgrade -y && python3 -m pip install --upgrade pip poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev
COPY . /app