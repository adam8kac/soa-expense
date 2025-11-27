FROM python:3.11-alpine

WORKDIR /app

RUN pip install --no-cache-dir fastapi uvicorn python-dotenv pydantic firebase-admin

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]