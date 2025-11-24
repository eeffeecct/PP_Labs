import asyncio
import logging
import random
import requests
import csv
import json
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FAVORITES_FILE = "favorites.json"

logging.basicConfig(level=logging.INFO)

shown_photos = {}
user_preferences = {}
photo_cache = {}  # Кэш для хранения информации о фото

# === Загрузка и сохранение любимых тем ===
def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_favorites():
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(user_preferences, f, ensure_ascii=False, indent=2)

# Загружаем при старте
user_preferences = load_favorites()

# === Клавиатура ===
main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton(text="Случайная фотография")],
        [KeyboardButton(text="Моя любимая тема")],
        [KeyboardButton(text="Установить любимую тему")]
    ]
)

def get_photo_keyboard(photo_id=None, query=None):
    kb = []
    if query:
        kb.append(InlineKeyboardButton(text="Ещё одно похожее", callback_data=f"more_{query}"))
    if photo_id:
        kb.append(InlineKeyboardButton(text="Скачать в полном качестве", callback_data=f"download_{photo_id}"))
    kb.append(InlineKeyboardButton(text="Случайная фотография", callback_data="random"))
    return InlineKeyboardMarkup(inline_keyboard=[kb])

# === API ===
def get_random_photo():
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"count": 1}, timeout=15
        )
        if r.status_code != 200:
            return None, "Ошибка загрузки", None
        data = r.json()[0]

        # Сохраняем информацию о фото в кэш
        photo_id = data["id"]
        photo_cache[photo_id] = {
            "regular_url": data["urls"]["regular"],
            "full_url": data["urls"]["full"],
            "download_url": data["links"]["download"],
            "author": data["user"]["name"],
            "description": data.get("alt_description") or "Фото"
        }

        return data["urls"]["regular"], f"{photo_cache[photo_id]['description']}\nАвтор: {data['user']['name']}", photo_id
    except Exception as e:
        logging.error(f"Error in get_random_photo: {e}")
        return None, "Не удалось загрузить фото", None

def get_photo_by_query(query: str, user_id: int):
    try:
        r = requests.get(
            "https://api.unsplash.com/search/photos",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"query": query, "per_page": 30, "orientation": "landscape"},
            timeout=15
        )
        if r.status_code != 200 or not r.json().get("results"):
            return None, "Ничего не найдено", None

        results = r.json()["results"]
        if user_id not in shown_photos:
            shown_photos[user_id] = {}
        if query not in shown_photos[user_id]:
            shown_photos[user_id][query] = set()

        shown = shown_photos[user_id][query]
        available = [p for p in results if p["id"] not in shown]
        if not available:
            shown.clear()
            available = results

        photo = random.choice(available)
        shown.add(photo["id"])

        # Сохраняем информацию о фото в кэш
        photo_id = photo["id"]
        photo_cache[photo_id] = {
            "regular_url": photo["urls"]["regular"],
            "full_url": photo["urls"]["full"],
            "download_url": photo["links"]["download"],
            "author": photo["user"]["name"],
            "description": photo.get("alt_description") or query
        }

        return photo["urls"]["regular"], f"{photo_cache[photo_id]['description']}\nАвтор: {photo['user']['name']}", photo_id
    except Exception as e:
        logging.error(f"Error in get_photo_by_query: {e}")
        return None, "Ошибка поиска", None

async def download_photo_by_url(photo_url, filename):
    """Скачивает фото по URL и возвращает временный файл"""
    try:
        response = requests.get(photo_url, timeout=15)
        if response.status_code == 200:
            # Создаем временный файл
            temp_file = f"temp_{filename}.jpg"
            with open(temp_file, 'wb') as f:
                f.write(response.content)
            return temp_file
        return None
    except Exception as e:
        logging.error(f"Error downloading photo: {e}")
        return None

# === Бот ===
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

def log(user_id, action, query=None):
    with open("log.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([user_id, action, query, datetime.now()])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Просто напиши любое слово — пришлю красивое фото\n\n"
        "Или используй кнопки:",
        reply_markup=main_kb
    )
    log(message.from_user.id, "start")

@dp.message(F.text == "Случайная фотография")
async def random_photo(message: types.Message):
    await message.answer("Ищу...")
    url, caption, photo_id = get_random_photo()
    if url:
        await message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id))
    else:
        await message.answer(caption)
    log(message.from_user.id, "random")

@dp.message(F.text == "Моя любимая тема")
async def favorite_photo(message: types.Message):
    theme = user_preferences.get(str(message.from_user.id), "nature")
    await message.answer(f"Ищу по любимой теме: {theme}...")
    url, caption, photo_id = get_photo_by_query(theme, message.from_user.id)
    if url:
        await message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, theme))
    else:
        await message.answer("Не найдено")
    log(message.from_user.id, "favorite", theme)

@dp.message(F.text == "Установить любимую тему")
async def set_favorite_start(message: types.Message):
    await message.answer("Напиши слово — станет твоей любимой темой:")

# === Главный обработчик: любое слово = поиск ===
@dp.message(F.text)
async def handle_any_text(message: types.Message):
    text = message.text.strip().lower()

    if text in ["случайная фотография", "моя любимая тема", "установить любимую тему"]:
        return

    # Установка любимой темы (ответ на сообщение бота)
    if message.reply_to_message and "напиши слово" in message.reply_to_message.text.lower():
        user_preferences[str(message.from_user.id)] = text
        save_favorites()
        await message.answer(f"Любимая тема сохранена: {text}")
        log(message.from_user.id, "set_favorite", text)
        return

    # Поиск по слову
    await message.answer("Ищу...")
    url, caption, photo_id = get_photo_by_query(text, message.from_user.id)
    if url:
        await message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, text))
    else:
        await message.answer("Ничего не найдено. Попробуй: cat, sunset, mountain, space")
    log(message.from_user.id, "search", text)

@dp.callback_query(F.data.startswith("more_"))
async def more_photo(call: types.CallbackQuery):
    query = call.data.split("_", 1)[1]
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Ищу ещё...")
    url, caption, photo_id = get_photo_by_query(query, call.from_user.id)
    if url:
        await call.message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, query))
    else:
        await call.message.answer("Больше нет новых фото")
    await call.answer()

@dp.callback_query(F.data.startswith("download_"))
async def download_photo(call: types.CallbackQuery):
    photo_id = call.data.split("_", 1)[1]

    if photo_id not in photo_cache:
        await call.answer("Фото больше не доступно", show_alert=True)
        return

    photo_info = photo_cache[photo_id]

    await call.answer("Скачиваю фото...")

    # Скачиваем фото
    temp_file = await download_photo_by_url(
        photo_info["full_url"],
        f"{photo_id}_{call.from_user.id}"
    )

    if temp_file:
        # Отправляем файл
        with open(temp_file, 'rb') as photo_file:
            await call.message.answer_document(
                types.BufferedInputFile(
                    photo_file.read(),
                    filename=f"photo_{photo_id}.jpg"
                ),
                caption=f"📸 {photo_info['description']}\n👤 Автор: {photo_info['author']}"
            )

        # Удаляем временный файл
        os.remove(temp_file)
    else:
        await call.message.answer("Не удалось скачать фото")

    await call.answer()

@dp.callback_query(F.data == "random")
async def inline_random(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Случайное фото...")
    url, caption, photo_id = get_random_photo()
    if url:
        await call.message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id))
    await call.answer()

async def main():
    if not os.path.exists("log.csv"):
        with open("log.csv", "w", encoding="utf-8") as f:
            csv.writer(f).writerow(["user_id", "action", "query", "timestamp"])

    print("Бот запущен — просто пиши слова!")
    while True:
        try:
            await dp.start_polling(bot, polling_timeout=30, timeout=90, skip_updates=True, relax=1.0)
        except Exception as e:
            print(f"Переподключение: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())