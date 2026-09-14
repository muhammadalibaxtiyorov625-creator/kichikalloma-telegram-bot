import json
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
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

# Boshqa barcha erkin savol va xabarlar (AI orqali aqlli javob va ElevenLabs jonli ovoz)
@router.message(F.text)
async def default_message_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    user_text = message.text.strip()
    user_text_lower = user_text.lower()

    if any(k in user_text_lower for k in ["startup", "loyiha", "sayyora", "shoxrux", "asoschi", "vikipediya"]):
        await startup_info_handler(message)
        return

    # AI orqali javob olish
    ai_reply = None
    try:
        from gemini_ai import ask_gemini
        ai_reply = ask_gemini(user_text)
    except Exception as e:
        logger.warning(f"AI so'rovida xatolik: {e}")

    if not ai_reply:
        ai_reply = f"Salom! <b>Kichik Alloma</b> ovozli Mini Appiga kirish uchun <b>'{t['btn_chat']}'</b> tugmasini bosing! 🎙️✨"

    # 1. Matnli javobni yuborish
    await message.answer(
        ai_reply,
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )

    # 2. ElevenLabs orqali jonli inson ovozida gapirish
    try:
        import os
        from elevenlabs_service import generate_voice
        audio_path = f"ai_voice_{user_id}.mp3"
        audio_file = generate_voice(ai_reply, output_path=audio_path)
        if audio_file and os.path.exists(audio_file):
            await message.answer_voice(
                voice=FSInputFile(audio_file),
                caption="🎙️ <i>Kichik Alloma AI ovozi</i>",
                parse_mode="HTML"
            )
            # Faylni tozalash
            try:
                os.remove(audio_file)
            except Exception:
                pass
    except Exception as err:
        logger.warning(f"ElevenLabs TTS yuborishda xatolik: {err}")


# Ovozli xabarlar kelganda yoki /voice komandasi
@router.message(Command("voice"))
@router.message(Command("ovoz"))
@router.message(F.voice)
async def default_voice_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    
    # 1. Agar foydalanuvchi ovozli xabar yuborgan bo'lsa (F.voice)
    if message.voice:
        local_ogg = f"user_voice_{user_id}_{message.message_id}.ogg"
        try:
            import os
            from elevenlabs_service import transcribe_voice, generate_voice
            from gemini_ai import ask_gemini

            # Telegramdan ovoz faylini yuklab olish
            file_info = await message.bot.get_file(message.voice.file_id)
            await message.bot.download_file(file_info.file_path, local_ogg)

            # ElevenLabs Scribe orqali tinglash (STT)
            user_spoken_text = transcribe_voice(local_ogg)

            # Yuklangan ovoz faylini o'chirish
            if os.path.exists(local_ogg):
                try:
                    os.remove(local_ogg)
                except Exception:
                    pass

            if user_spoken_text and len(user_spoken_text.strip()) > 1:
                # AI orqali aqlli va to'liq javob olish
                ai_reply = ask_gemini(user_spoken_text)

                reply_caption = (
                    f"👂 <b>Sizni eshitdim:</b> <i>\"{user_spoken_text}\"</i>\n\n"
                    f"{ai_reply}"
                )

                # Matnli javob
                await message.answer(
                    reply_caption,
                    reply_markup=get_main_keyboard(lang),
                    parse_mode="HTML"
                )

                # ElevenLabs orqali jonli ovozda qaytarish
                reply_audio_path = f"ai_voice_reply_{user_id}.mp3"
                audio_file = generate_voice(ai_reply, output_path=reply_audio_path)
                if audio_file and os.path.exists(audio_file):
                    await message.answer_voice(
                        voice=FSInputFile(audio_file),
                        caption="🎙️ <i>Kichik Alloma AI javobi</i>",
                        parse_mode="HTML"
                    )
                    try:
                        os.remove(audio_file)
                    except Exception:
                        pass
                return

        except Exception as err:
            logger.warning(f"Ovozli xabarni qayta ishlashda xatolik: {err}")
            if os.path.exists(local_ogg):
                try:
                    os.remove(local_ogg)
                except Exception:
                    pass

    # 2. Agar /voice yoki /ovoz komandasi bo'lsa yoki ovoz tanilmasa
    try:
        import os
        from elevenlabs_service import generate_voice
        voice_text = (
            "Salom, qadrdon kichik allomam! Men sizning sun'iy intellekt ustozi va do'stingizman. "
            "Menga xohlagan savolingizni ovozli xabar orqali yuboring, barchasini diqqat bilan eshitib, "
            "inson ovozida batafsil javob beraman!"
        )
        audio_path = f"voice_intro_{user_id}.mp3"
        audio_file = generate_voice(voice_text, output_path=audio_path)
        if audio_file and os.path.exists(audio_file):
            await message.answer_voice(
                voice=FSInputFile(audio_file),
                caption=f"🎙️ <b>Kichik Alloma AI (Jonli ovoz):</b>\n\n{voice_text}\n\nMini App orqali to'liq suhbatlashish uchun <b>'{t['btn_chat']}'</b> tugmasini bosing! 🌟",
                reply_markup=get_main_keyboard(lang),
                parse_mode="HTML"
            )
            try:
                os.remove(audio_file)
            except Exception:
                pass
            return
    except Exception as e:
        logger.warning(f"Voice generation error: {e}")

    await message.answer(
        f"Ovozli xabaringiz qabul qilindi! 🎙️✨\n\nJonli ovozli suhbatlashish uchun pastdagi <b>'{t['btn_chat']}'</b> tugmasini bosing!",
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )
