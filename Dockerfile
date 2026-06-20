FROM python:3.14

WORKDIR /app

COPY requirements.txt ./

COPY .env ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./WebApp/brickDjangoBackend/ .

EXPOSE 8000

ENTRYPOINT ["python", "./manage.py", "runserver", "0.0.0.0:8000"]
