from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from locales import TEXTS, get_user_lang
from planets_service import get_all_planets

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

def get_planets_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    planets = get_all_planets(lang=lang)
    emojis = {
        185: "🌍", 186: "🔴", 187: "🔵", 188: "🟡",
        189: "🌊", 190: "🪐", 191: "🟣", 192: "🟠"
    }
    keyboard = []
    row = []
    for p in planets:
        title = p.get("title", "Sayyora")
        p_id = p.get("id")
        emo = emojis.get(int(p_id), "🪐")
        row.append(InlineKeyboardButton(text=f"{emo} {title}", callback_data=f"planet_view:{p_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    back_text = t.get("btn_back", "🔙 Orqaga")
    keyboard.append([InlineKeyboardButton(text=back_text, callback_data="close_planets")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_single_planet_keyboard(current_planet_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    t = TEXTS.get(lang, TEXTS["uz"])
    planets = get_all_planets(lang=lang)
    emojis = {
        185: "🌍", 186: "🔴", 187: "🔵", 188: "🟡",
        189: "🌊", 190: "🪐", 191: "🟣", 192: "🟠"
    }
    keyboard = []
    row = []
    for p in planets:
        p_id = p.get("id")
        title = p.get("title", "Sayyora")
        emo = emojis.get(int(p_id), "🪐")
        is_cur = str(p_id) == str(current_planet_id)
        btn_text = f"✨ {emo} {title}" if is_cur else f"{emo} {title}"
        row.append(InlineKeyboardButton(text=btn_text, callback_data=f"planet_view:{p_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    all_planets_text = t.get("btn_all_planets", "🪐 Barcha sayyoralar")
    back_text = t.get("btn_back", "🔙 Orqaga")
    keyboard.append([
        InlineKeyboardButton(text=all_planets_text, callback_data="planets_menu"),
        InlineKeyboardButton(text=back_text, callback_data="close_planets")
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
