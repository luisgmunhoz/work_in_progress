# next app docker file from python:3.8
FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN mkdir /code

WORKDIR /code
COPY requirements.txt /code/
RUN python3 -m pip install -r requirements.txt

COPY . /code/
EXPOSE 8000