FROM python:3.8-alpine
WORKDIR /app
COPY . /app
RUN pip install pipenv
RUN pipenv install
