FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=1000 --retries 10 --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3008

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3008", "--reload", "--log-level", "debug"]