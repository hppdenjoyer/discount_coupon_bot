FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir python-telegram-bot==20.7 telegram>=0.0.1

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
