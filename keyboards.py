from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from locales import TEXTS, get_user_lang, get_user_age

# Internetda jonli ishlayotgan Mini App HTTPS manzili
DEFAULT_WEBAPP_URL = "https://kichikalloma-bot.surge.sh"

def get_main_keyboard(lang: str = "uz", webapp_url: str = None) -> ReplyKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    url = webapp_url or DEFAULT_WEBAPP_URL

    keyboard = [
        [
            KeyboardButton(
                text=t["btn_chat"],
                web_app=WebAppInfo(url=url)
            )
        ],
        [
            KeyboardButton(text=t["btn_help"]),
            KeyboardButton(text=t["btn_settings"])
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Kerakli bo'limni tanlang..."
    )

def get_cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    placeholder = (
        "✍️ Muammo yoki savolingizni yozing..." if lang == "uz"
        else ("✍️ Напишите ваш вопрос или проблему..." if lang == "ru"
        else "✍️ Type your message here...")
    )
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t["cancel"])]],
        resize_keyboard=True,
        input_field_placeholder=placeholder
    )

def get_settings_keyboard(user_id: int) -> InlineKeyboardMarkup:
    current_lang = get_user_lang(user_id)
    current_age = get_user_age(user_id)

    def mark(cond: bool, label: str) -> str:
        return f"✅ {label}" if cond else label

    # Faqat tillar va yosh toifalari (Sekin/Oddiy tezlik olib tashlandi)
    keyboard = [
        [
            InlineKeyboardButton(
                text=mark(current_lang == "uz", "🇺🇿 O'zbek"),
                callback_data="set_lang:uz"
            ),
            InlineKeyboardButton(
                text=mark(current_lang == "ru", "🇷🇺 Русский"),
                callback_data="set_lang:ru"
            ),
            InlineKeyboardButton(
                text=mark(current_lang == "en", "🇬🇧 English"),
                callback_data="set_lang:en"
            ),
        ],
        [
            InlineKeyboardButton(
                text=mark(current_age == "7-8", "🧒 7-8 yosh"),
                callback_data="set_age:7-8"
            ),
            InlineKeyboardButton(
                text=mark(current_age == "9-11", "👦 9-11 yosh"),
                callback_data="set_age:9-11"
            ),
        ],
        [
            InlineKeyboardButton(text="🔙 Yopish", callback_data="close_settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
