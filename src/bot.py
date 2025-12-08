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
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from dotenv import load_dotenv
import aiohttp

load_dotenv()

UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")
FAVORITES_FILE = "favorites.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

shown_photos = {}
user_preferences = {}
photo_cache = {}
user_states = {}

def load_favorites():
    if not os.path.exists(FAVORITES_FILE):
        logging.info("Favorites file does not exist. Starting with empty preferences.")
        return {}

    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {FAVORITES_FILE}. File might be empty or corrupted.")
        return {}
    except Exception as e:
        logging.error(f"Unexpected error loading favorites: {e}")
        return {}

def save_favorites():
    try:
        with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
            json.dump(user_preferences, f, ensure_ascii=False, indent=2)
        logging.info(f"Successfully saved {len(user_preferences)} favorites to {FAVORITES_FILE}")
    except Exception as e:
        logging.error(f"Error saving favorites to {FAVORITES_FILE}: {e}")

user_preferences = load_favorites()

def log(user_id, action, query=None):
    with open("log.csv", "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([user_id, action, query, datetime.now()])

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

def get_random_photo():
    try:
        r = requests.get(
            "https://api.unsplash.com/photos/random",
            headers={"Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"},
            params={"count": 1}, timeout=15
        )
        if r.status_code != 200:
            logging.error(f"Unsplash API returned status {r.status_code} for random photo.")
            return None, "Ошибка загрузки", None

        data = r.json()[0]
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
        if r.status_code != 200:
            logging.error(f"Unsplash API returned status {r.status_code} for query: {query}")
            return None, "Ошибка поиска", None

        results = r.json().get("results")
        if not results:
            return None, "Ничего не найдено", None

        if user_id not in shown_photos:
            shown_photos[user_id] = {}
        if query not in shown_photos[user_id]:
            shown_photos[user_id][query] = set()

        shown = shown_photos[user_id][query]
        available = [p for p in results if p["id"] not in shown]

        if not available:
            logging.info(f"Clearing shown photos cache for user {user_id}, query {query}.")
            shown.clear()
            available = results

        photo = random.choice(available)
        shown.add(photo["id"])
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

def get_progress_bar(percent):
    bar_length = 10
    filled = int(bar_length * percent / 100)
    bar = '█' * filled + '░' * (bar_length - filled)
    return f"Скачиваю фото: [{bar}] {percent}%"

async def download_photo_by_url(photo_url, photo_id, user_id, progress_msg):
    temp_file = f"temp_{photo_id}_{user_id}.jpg"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(photo_url, timeout=30) as resp:
                if resp.status != 200:
                    logging.error(f"Failed to fetch photo from URL: {photo_url}")
                    return None
                total_size = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                last_percent = 0
                with open(temp_file, 'wb') as f:
                    async for chunk in resp.content.iter_chunked(1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = min(100, int((downloaded / total_size) * 100))
                                if percent >= last_percent + 5 or percent == 100:
                                    await progress_msg.edit_text(get_progress_bar(percent))
                                    last_percent = percent
                return temp_file
    except Exception as e:
        logging.error(f"Error during photo download: {e}")
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return None

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

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
    user_id_str = str(message.from_user.id)

    if user_id_str not in user_preferences:
        await message.answer("У вас нет любимой темы. Добавьте ее с помощью кнопки 'Установить любимую тему'!")
        return

    theme = user_preferences[user_id_str]
    await message.answer(f"Ищу по любимой теме: {theme}...")
    url, caption, photo_id = get_photo_by_query(theme, message.from_user.id)
    if url:
        await message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, theme))
    else:
        await message.answer(f"Не найдено фото по любимой теме: {theme}")
    log(message.from_user.id, "favorite", theme)

@dp.message(F.text == "Установить любимую тему")
async def set_favorite_start(message: types.Message):
    user_states[message.from_user.id] = "setting_favorite"
    await message.answer("Напиши слово или фразу — она станет твоей любимой темой:")

@dp.message(F.text)
async def handle_any_text(message: types.Message):
    text = message.text.strip()

    if text in ["Случайная фотография", "Моя любимая тема", "Установить любимую тему"]:
        return

    if message.from_user.id in user_states and user_states[message.from_user.id] == "setting_favorite":
        theme = text.lower()
        user_preferences[str(message.from_user.id)] = theme
        save_favorites()
        await message.answer(f"✅ Любимая тема сохранена: {theme}")
        log(message.from_user.id, "set_favorite", theme)
        del user_states[message.from_user.id]
        return

    query = text.lower()
    await message.answer(f"Ищу по запросу: {query}...")
    url, caption, photo_id = get_photo_by_query(query, message.from_user.id)
    if url:
        await message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, query))
    else:
        await message.answer("Ничего не найдено. Попробуй: cat, sunset, mountain, space")
    log(message.from_user.id, "search", query)

@dp.callback_query(F.data.startswith("more_"))
async def more_photo(call: types.CallbackQuery):
    query = call.data.split("_", 1)[1]

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(f"Ищу ещё по запросу: {query}...")
    url, caption, photo_id = get_photo_by_query(query, call.from_user.id)

    if url:
        await call.message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id, query))
    else:
        await call.message.answer("Больше нет новых фото, сбросил кэш. Попробуй еще раз.")

    await call.answer()
    log(call.from_user.id, "more_photo", query)

@dp.callback_query(F.data.startswith("download_"))
async def download_photo(call: types.CallbackQuery):
    photo_id = call.data.split("_", 1)[1]

    if photo_id not in photo_cache:
        await call.answer("Фото больше не доступно в кэше", show_alert=True)
        return

    photo_info = photo_cache[photo_id]

    await call.answer("Начинаю скачивание в полном качестве...", show_alert=False)

    progress_msg = await call.message.answer(get_progress_bar(0))

    temp_file = await download_photo_by_url(
        photo_info["full_url"],
        photo_id,
        call.from_user.id,
        progress_msg
    )

    if temp_file:
        try:
            await call.message.answer_document(
                FSInputFile(temp_file),
                caption=f"📸 {photo_info['description']}\n👤 Автор: {photo_info['author']}"
            )
        except Exception as e:
            await call.message.answer(f"Не удалось отправить файл: {e}")
            logging.error(f"Failed to send document: {e}")
        finally:
            os.remove(temp_file)
            await progress_msg.delete()
    else:
        await progress_msg.edit_text("Не удалось скачать фото.")

    log(call.from_user.id, "download", photo_id)

@dp.callback_query(F.data == "random")
async def inline_random(call: types.CallbackQuery):
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer("Случайное фото...")
    url, caption, photo_id = get_random_photo()
    if url:
        await call.message.answer_photo(url, caption=caption, reply_markup=get_photo_keyboard(photo_id))
    await call.answer()
    log(call.from_user.id, "inline_random")

async def main():
    if not os.path.exists("log.csv"):
        with open("log.csv", "w", encoding="utf-8") as f:
            csv.writer(f).writerow(["user_id", "action", "query", "timestamp"])

    logging.info("Бот запущен — просто пиши слова!")

    while True:
        try:
            await dp.start_polling(bot, polling_timeout=30, timeout=90, skip_updates=True, relax=1.0)
        except Exception as e:
            logging.error(f"Ошибка в цикле polling. Переподключение через 5 секунд: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())