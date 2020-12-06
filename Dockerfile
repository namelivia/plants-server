FROM python:3.8-alpine
WORKDIR /app
COPY . /app
# install psycopg2 dependencies
RUN apk update
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install pipenv
#TODO: For production this should change
RUN pipenv install --dev
#TODO: And also this, probably different Dockerfiles
EXPOSE 4444
