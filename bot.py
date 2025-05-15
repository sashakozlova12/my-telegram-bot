from dotenv import load_dotenv
import os
load_dotenv()

import asyncio
import re
import google.generativeai as genai
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties

# 🔐 Конфигурация (замени на os.environ при деплое в продакшн)
import os

TOKEN_API = os.getenv("TOKEN_API")  # Получаем токен из переменной окружения
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # API ключ тоже из окружения

MODEL_NAME = "gemini-2.0-flash"

# 📌 Команды бота
HELP_COMMAND = """
<b>Вот что я умею!</b>
/hi - поздороваться со мной
/help - напомнить список моих команд
/ask &lt;твой вопрос&gt; - задай  мне вопрос 
"""

# 🤖 Инициализация бота с HTML parse_mode
bot = Bot(token=TOKEN_API, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# 🔧 Настройка Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# 🔄 Конвертация Markdown в HTML для Telegram
def convert_markdown_to_html(markdown_text: str) -> str:
    html_text = markdown_text
    html_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", html_text)    # жирный
    html_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", html_text)        # *курсив*
    html_text = re.sub(r"\n[-*] (.*?)", r"\n• \1", html_text)        # списки
    return html_text

# 💬 Запрос к Google Gemini (асинхронный)
async def query_llm(user_message: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # generate_content синхронный, запускаем в отдельном потоке:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, model.generate_content, user_message)
        if hasattr(response, "text"):
            return convert_markdown_to_html(response.text.strip())
        else:
            return "Генрих говорит, что ответа пока нет 🤷‍♂️"
    except Exception as e:
        return f"Ошибка при запросе к ИИ: {e}"

# Команда /hi —  здоровается
@dp.message(Command("hi"))
async def start_command(message: Message):
    await message.answer(
        "<em>Привет!, твой верный помощник и весёлый собеседник!</em>\n"
        "Напиши /help, если хочешь узнать, что я умею."
    )

# Команда /помоги — список команд
@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(HELP_COMMAND)

# Команда /спроси — задаём вопрос ИИ
@dp.message(Command("ask"))
async def ask_command(message: Message):
    user_input = message.text.removeprefix("/ask").strip()
    if not user_input:
        await message.answer(" Напиши вопрос после команды /ask")
        return
    response = await query_llm(user_input)
    await message.answer(response)

# Запуск бота
async def main():
    print("✅ Бот на связи! Бот запущен!")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())