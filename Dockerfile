FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY pyproject.toml .
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Копирование исходного кода
COPY . .

# Настройка переменных окружения
ENV PYTHONUNBUFFERED=1

# Запуск бота
CMD ["python", "main.py"]
