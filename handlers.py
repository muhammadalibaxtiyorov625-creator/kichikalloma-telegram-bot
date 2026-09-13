import json
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import SupportState
from locales import TEXTS, get_user_lang, set_user_setting
from keyboards import (
    get_main_keyboard,
    get_settings_keyboard,
    get_cancel_keyboard
)

logger = logging.getLogger(__name__)
router = Router()

# /start komandasi va "🔄 Boshlash (/start)" tugmasi
@router.message(CommandStart())
@router.message(F.text.in_([
    "🔄 Boshlash (/start)",
    "🔄 Старт (/start)",
    "🔄 Start (/start)",
    "Boshlash",
    "/start"
]))
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    user_name = message.from_user.first_name or "Do'stim"

    welcome_text = t["welcome"].format(name=user_name)
    await message.answer(
        welcome_text,
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )

# /help komandasi va "🆘 Yordam (/help)" tugmasi
@router.message(Command("help"))
@router.message(F.text.in_([
    "🆘 Yordam (/help)",
    "🆘 Помощь (/help)",
    "🆘 Help (/help)",
    "🆘 Yordam / Bog'lanish",
    "ℹ️ Yordam",
    "Yordam",
    "/help"
]))
async def help_button_handler(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])

    await state.set_state(SupportState.waiting_for_help_message)
    await message.answer(
        t["help_intro"],
        reply_markup=get_cancel_keyboard(lang),
        parse_mode="HTML"
    )

# Bekor qilish tugmasi bosilganda
@router.message(SupportState.waiting_for_help_message, F.text.in_(["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]))
async def cancel_support_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    await message.answer(
        "❌ Bekor qilindi. Asosiy menyudasiz.",
        reply_markup=get_main_keyboard(lang)
    )

# Foydalanuvchi yordam so'rab matn yozib jo'natganda
@router.message(SupportState.waiting_for_help_message, F.text)
async def process_support_message(message: Message, state: FSMContext) -> None:
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
    user_text = message.text
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])

    # Log qilish
    logger.info(
        f"\n[YANGI YORDAM XABARI] Foydalanuvchi: {user_name} ({username})\n"
        f"Matn: {user_text}\n"
        f"Admin @v_shoxrux ga yo'naltirilgan.\n"
    )

    await state.clear()

    await message.answer(
        t["help_sent"],
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )

# /settings komandasi va Sozlamalar tugmasi
@router.message(Command("settings"))
@router.message(F.text.in_([
    "⚙️ Sozlamalar",
    "⚙️ Настройки",
    "⚙️ Settings",
    "/settings"
]))
async def settings_button_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])

    await message.answer(
        t["settings_title"],
        reply_markup=get_settings_keyboard(user_id),
        parse_mode="HTML"
    )

# Tilni o'zgartirish callback
@router.callback_query(F.data.startswith("set_lang:"))
async def change_lang_callback(callback: CallbackQuery) -> None:
    new_lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    set_user_setting(user_id, "lang", new_lang)
    await callback.answer(f"Til o'zgartirildi: {new_lang.upper()} ✅")

    t = TEXTS.get(new_lang, TEXTS["uz"])
    try:
        await callback.message.edit_text(
            t["settings_title"],
            reply_markup=get_settings_keyboard(user_id),
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    await callback.message.answer(
        "Menyu yangilandi / Меню обновлено / Menu updated!",
        reply_markup=get_main_keyboard(new_lang)
    )

# Yosh toifasini o'zgartirish
@router.callback_query(F.data.startswith("set_age:"))
async def change_age_callback(callback: CallbackQuery) -> None:
    age = callback.data.split(":")[1]
    user_id = callback.from_user.id
    set_user_setting(user_id, "age", age)
    await callback.answer(f"Tanlangan yosh: {age} yosh ✅", show_alert=True)
    try:
        await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(user_id))
    except Exception:
        pass

# Talaffuz tezligini o'zgartirish
@router.callback_query(F.data.startswith("set_speed:"))
async def change_speed_callback(callback: CallbackQuery) -> None:
    speed = callback.data.split(":")[1]
    user_id = callback.from_user.id
    set_user_setting(user_id, "speed", speed)
    msg = "🐢 Sekin talaffuz yoqildi" if speed == "slow" else "🐇 Oddiy tezlik yoqildi"
    await callback.answer(msg, show_alert=True)
    try:
        await callback.message.edit_reply_markup(reply_markup=get_settings_keyboard(user_id))
    except Exception:
        pass

# Sozlamalarni yopish
@router.callback_query(F.data == "close_settings")
async def close_settings_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.delete()

# Mini App dan qaytgan ma'lumotlar
@router.message(F.web_app_data)
async def webapp_data_handler(message: Message) -> None:
    raw_data = message.web_app_data.data
    try:
        data = json.loads(raw_data)
        stars = data.get("stars", 3)
        score = data.get("score", 100)
        topic = data.get("topic", "English Chat Practice")

        congrats_text = (
            f"🎉 <b>Super! Barakalla, {message.from_user.first_name}!</b> 🌟\n\n"
            f"📚 Mavzu: <b>{topic}</b>\n"
            f"⭐ Yulduzchalar: {'⭐' * stars}\n"
            f"🎯 Ball: <b>{score} / 100</b>\n\n"
            f"Ingliz tilida gapirishni a'lo bajarding! Yana mashq qilish uchun pastdagi "
            f"<b>'🎙️ Inglizcha Suhbat'</b> tugmasini bosing!"
        )
        await message.answer(congrats_text, parse_mode="HTML")
    except Exception:
        await message.answer("✅ Mashg'ulot natijalari muvaffaqiyatli saqlandi! Barakalla! 🌟")

# /about, /startup, /sayyoralar komandalari
@router.message(Command("startup"))
@router.message(Command("about"))
@router.message(Command("sayyoralar"))
@router.message(F.text.lower().in_([
    "startup", "start up", "loyiha", "loyihasi", "haqida", "sayyoralar", "8 ta sayyora", "asoschi", "muallif"
]))
async def startup_info_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    info_text = (
        "🚀 <b>Kichik Alloma — 8 Sayyorali Rivojlanish Ekotizimi</b>\n\n"
        "<b>Kichik Alloma</b> — bu 7–11 yoshdagi bolalar va ota-onalar uchun mo'ljallangan "
        "AI asosidagi ta'lim va rivojlanish ekotizimidir.\n\n"
        "🎯 <b>Loyiha Maqsadi va Konsepsiyasi:</b>\n"
        "Bola kosmik xaritadagi 8 ta sayyoraga sayohat qiladi va har bir sayyora bitta aniq vazifani bajaradi:\n\n"
        "• 🌍 <b>Yer (Kognitiv ta’lim + AI Tutor):</b> Sokratik usulda ta'lim beruvchi AI bilan kunlik 20 daqiqalik muloqot limiti.\n"
        "• 🟠 <b>Yupiter (O‘z-o‘zini boshqarish):</b> Kunni rejalashtirish, vazifalarni bajarish va intizom.\n"
        "• 🟡 <b>Venera (Virtual Store):</b> 'Gold Coin' oltin tangalari evaziga avatar va buyumlar do'koni.\n"
        "• 🪐 <b>Saturn (Matematika + mantiq):</b> Matematik misollar, mantiqiy savollar va testlar.\n"
        "• 🪐 <b>Merkuriy (Ijodkorlik + kasblar):</b> Kasblar haqida videolar va ijodkorlik.\n"
        "• 🔵 <b>Uran (English Vocabulary):</b> Inglizcha so'zlar, rasm va to'g'ri audio talaffuz.\n"
        "• 🔴 <b>Mars (Jismoniy faollik):</b> Jismoniy harakat va sog'lom mashqlar.\n"
        "• 🌊 <b>Neptun (Emotsional savodxonlik):</b> Hissiyotlarni tanish, xavfsiz makon.\n\n"
        "🛡️ <b>Xavfsizlik:</b> Parent Dashboard, bolalar xavfsizligi, diagnostika/tibbiy xulosa bermaydi.\n"
        "👨‍💻 <b>Asoschi (Founder & Lead Developer):</b> Komiljonov Shoxruxbek Komiljon o'g'li\n"
        "🌐 <b>Rasmiy veb-sayt:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
        "📖 <b>Vikipediya sahifasi:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Startup maqolasi</a>\n\n"
        "Suhbatlashish uchun pastdagi tugmani bosing! 👇"
    )
    await message.answer(info_text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")

# Boshqa xabarlar
@router.message()
async def default_message_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    user_text = (message.text or "").lower()

    if any(k in user_text for k in ["startup", "loyiha", "sayyora", "shoxrux", "asoschi", "vikipediya", "alloma"]):
        await startup_info_handler(message)
        return

    await message.answer(
        f"Salom! <b>Kichik Alloma</b> ovozli Mini Appiga kirish uchun <b>'{t['btn_chat']}'</b> tugmasini bosing! 🎙️✨",
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )
