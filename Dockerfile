FROM python:3.14

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY ./WebApp/brickDjangoBackend/ .

EXPOSE 8000

# The backend reads FUSEKI_* and MONGODB_ENDPOINT from the environment. Pass
# them at run time instead of baking them into the image:
#   docker build -t brick-backend .
#   docker run --env-file .env -p 8000:8000 brick-backend
ENTRYPOINT ["python", "./manage.py", "runserver", "0.0.0.0:8000"]
