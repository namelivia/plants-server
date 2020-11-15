FROM python:3.8-alpine
WORKDIR /app
COPY . /app
# install psycopg2 dependencies
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install pipenv
RUN pipenv install --dev
EXPOSE 4444
