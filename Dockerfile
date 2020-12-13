FROM python:3.8-alpine AS builder
WORKDIR /app
COPY . /app
RUN apk update
# psycopg2 dependencies
RUN apk add postgresql-dev gcc python3-dev musl-dev
RUN pip install pipenv

FROM builder AS development
RUN pipenv install --dev
EXPOSE 4444

FROM builder AS production
RUN pipenv install
CMD ["pipenv", "run", "gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker" , "app.main:app"]
