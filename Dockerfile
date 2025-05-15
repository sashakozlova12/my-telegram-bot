# Используем официальный Python 3.11 slim образ
FROM python:3.11-slim

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Задаём переменные окружения (можно переопределить при запуске)
ENV TOKEN_API=your_token_here
ENV GEMINI_API_KEY=your_gemini_key_here

# Команда запуска
CMD ["python", "bot.py"]

