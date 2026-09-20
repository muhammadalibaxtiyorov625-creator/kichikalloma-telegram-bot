from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from locales import TEXTS, get_user_lang

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
            KeyboardButton(text=t["btn_math"]),
            KeyboardButton(text=t["btn_english"])
        ],
        [
            KeyboardButton(text=t["btn_planets"])
        ],
        [
            KeyboardButton(text=t["btn_help"]),
            KeyboardButton(text=t["btn_settings"])
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=t.get("input_placeholder", "Savol yozing yoki bo'limni tanlang...")
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
    t = TEXTS.get(current_lang, TEXTS["uz"])

    def mark(cond: bool, label: str) -> str:
        return f"✅ {label}" if cond else label

    # Faqat tillar bo'limi (Foydalanuvchi talabi: Yosh toifalari olib tashlandi, faqat tillar qoldirildi)
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
            InlineKeyboardButton(text=t.get("btn_close", "🔙 Yopish"), callback_data="close_settings")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
