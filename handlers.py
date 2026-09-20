import os
import json
import asyncio
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.enums import ChatAction
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

async def _async_send_voice_note(message: Message, text: str, user_id: int, lang: str = None) -> None:
    """Fon rejimida tanlangan tildagi o'g'il bola ovozini yaratib yuborish"""
    try:
        if not lang:
            lang = get_user_lang(user_id)
        from elevenlabs_service import generate_voice
        await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.RECORD_VOICE)
        audio_path = f"ai_voice_{user_id}_{message.message_id}.mp3"
        audio_file = await asyncio.to_thread(generate_voice, text, audio_path, lang)
        if audio_file and os.path.exists(audio_file):
            caption = "🎙️ <i>Kichik Alloma AI ovozi</i>" if lang == "uz" else ("🎙️ <i>Голос Kichik Alloma AI</i>" if lang == "ru" else "🎙️ <i>Kichik Alloma AI Voice</i>")
            await message.answer_voice(
                voice=FSInputFile(audio_file),
                caption=caption,
                parse_mode="HTML"
            )
            try:
                os.remove(audio_file)
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Async voice generation xatosi: {e}")

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
    voice_greeting = "Assalomu alaykum, do'stim! Kichik Alloma koinotiga xush kelibsiz!" if lang == "uz" else ("Привет, мой юный друг! Добро пожаловать во вселенную Kichik Alloma!" if lang == "ru" else "Hello my friend! Welcome to the Kichik Alloma universe!")
    asyncio.create_task(_async_send_voice_note(message, voice_greeting, user_id, lang=lang))

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
    cancel_msg = "❌ Bekor qilindi. Asosiy menyudasiz." if lang == "uz" else ("❌ Отменено. Вы в главном меню." if lang == "ru" else "❌ Cancelled. You are in the main menu.")
    await message.answer(
        cancel_msg,
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

# Tilni o'zgartirish callback — FAQAT TILLAR, DARHOL HAMMA MENYU VA OVOZ SHU TILGA O'TADI!
@router.callback_query(F.data.startswith("set_lang:"))
async def change_lang_callback(callback: CallbackQuery) -> None:
    new_lang = callback.data.split(":")[1]
    user_id = callback.from_user.id
    set_user_setting(user_id, "lang", new_lang)
    
    alert_text = "Til o'zgartirildi: O'ZBEKCHA ✅" if new_lang == "uz" else ("Язык изменен: РУССКИЙ ✅" if new_lang == "ru" else "Language changed: ENGLISH ✅")
    await callback.answer(alert_text)

    t = TEXTS.get(new_lang, TEXTS["uz"])
    try:
        await callback.message.edit_text(
            t["settings_title"],
            reply_markup=get_settings_keyboard(user_id),
            parse_mode="HTML"
        )
    except Exception:
        pass
    
    # Asosiy klaviaturani ham darhol yangi tilga o'tkazish
    await callback.message.answer(
        t["lang_changed_msg"],
        reply_markup=get_main_keyboard(new_lang),
        parse_mode="HTML"
    )
    asyncio.create_task(_async_send_voice_note(callback.message, t["lang_changed_msg"], user_id, lang=new_lang))

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
        topic = data.get("topic", "Learning Practice")

        congrats_text = (
            f"🎉 <b>Super! Barakalla, {message.from_user.first_name}!</b> 🌟\n\n"
            f"📚 Mavzu: <b>{topic}</b>\n"
            f"⭐ Yulduzchalar: {'⭐' * stars}\n"
            f"🎯 Ball: <b>{score} / 100</b>\n\n"
            f"Mashg'ulotni a'lo bajardingiz! Yana davom ettirish uchun pastdagi tugmalardan foydalaning!"
        )
        await message.answer(congrats_text, parse_mode="HTML")
    except Exception:
        await message.answer("✅ Mashg'ulot natijalari muvaffaqiyatli saqlandi! Barakalla! 🌟")

# /about, /startup komandalari — Asoschi Shoxrux Komiljonov va uning jamoasi
@router.message(Command("startup"))
@router.message(Command("about"))
@router.message(F.text.lower().in_([
    "startup", "start up", "loyiha", "loyihasi", "haqida", "asoschi", "muallif",
    "о проекте", "основатель", "кто создал", "about", "founder"
]))
async def startup_info_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if lang == "ru":
        info_text = (
            "🚀 <b>Kichik Alloma — Образовательная экосистема из 8 планет для детей 7–11 лет</b>\n\n"
            "👨‍💻 <b>Основатель (Founder):</b> Шохрух Комилджонов и его талантливая команда\n"
            "🌐 <b>Официальный сайт:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
            "📖 <b>Статья в Википедии:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Startup maqolasi</a>\n\n"
            "🪐 <b>8 Планет экосистемы:</b>\n"
            "• 🌍 <b>Земля:</b> AI Tutor и когнитивное развитие\n"
            "• 🟠 <b>Юпитер:</b> Самодисциплина и тайм-менеджмент\n"
            "• 🟡 <b>Венера:</b> Виртуальный магазин за Gold Coins\n"
            "• 🪐 <b>Сатурн:</b> Математика, счет и логические задачи\n"
            "• 🟣 <b>Меркурий:</b> Творчество и профессии будущего\n"
            "• 🔵 <b>Уран:</b> Английский язык и словарный запас\n"
            "• 🔴 <b>Марс:</b> Физическая активность и упражнения\n"
            "• 🌊 <b>Нептун:</b> Эмоциональная грамотность и чувства\n\n"
            "🛡️ <b>Безопасность:</b> Родительский контроль, безопасный лимит AI 20 минут в день!"
        )
    elif lang == "en":
        info_text = (
            "🚀 <b>Kichik Alloma — 8-Planet Educational Ecosystem for Kids 7–11</b>\n\n"
            "👨‍💻 <b>Founder & Lead:</b> Shoxrux Komiljonov and his dedicated team\n"
            "🌐 <b>Official Website:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
            "📖 <b>Wikipedia:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Startup Article</a>\n\n"
            "🪐 <b>8 Cosmic Planets:</b>\n"
            "• 🌍 <b>Earth:</b> AI Tutor & Cognitive Education\n"
            "• 🟠 <b>Jupiter:</b> Self-discipline and daily routines\n"
            "• 🟡 <b>Venus:</b> Virtual Gold Coin Store\n"
            "• 🪐 <b>Saturn:</b> Mathematics and Logic puzzles\n"
            "• 🟣 <b>Mercury:</b> Creativity and Future Careers\n"
            "• 🔵 <b>Uranus:</b> English Vocabulary & Pronunciation\n"
            "• 🔴 <b>Mars:</b> Physical fitness and movement\n"
            "• 🌊 <b>Neptune:</b> Emotional intelligence & feelings\n\n"
            "🛡️ <b>Safety:</b> Parent Dashboard, safe 20-min daily limit!"
        )
    else:
        info_text = (
            "🚀 <b>Kichik Alloma — 8 Sayyorali Rivojlanish Ekotizimi</b>\n\n"
            "👨‍💻 <b>Asoschi (Founder & Lead Developer):</b> Shoxrux Komiljonov va uning jamoasi\n"
            "🌐 <b>Rasmiy veb-sayt:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
            "📖 <b>Vikipediya sahifasi:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Startup maqolasi</a>\n\n"
            "🪐 <b>8 ta Sayyora Ekotizimi:</b>\n"
            "• 🌍 <b>Yer (Kognitiv ta’lim + AI Tutor):</b> Sokratik usulda ta'lim beruvchi AI\n"
            "• 🟠 <b>Yupiter (O‘z-o‘zini boshqarish):</b> Kunni rejalashtirish va intizom\n"
            "• 🟡 <b>Venera (Virtual Store):</b> Gold Coin evaziga do'kon\n"
            "• 🪐 <b>Saturn (Matematika + mantiq):</b> Tezkor misollar va testlar\n"
            "• 🟣 <b>Merkuriy (Ijodkorlik + kasblar):</b> Ijodiyot va kelajak kasblari\n"
            "• 🔵 <b>Uran (English Vocabulary):</b> Inglizcha so'zlar va to'g'ri talaffuz\n"
            "• 🔴 <b>Mars (Jismoniy faollik):</b> Jismoniy harakat va sport\n"
            "• 🌊 <b>Neptun (Emotsional savodxonlik):</b> Hissiyotlarni tanish va mehr\n\n"
            "🛡️ <b>Xavfsizlik:</b> Parent Dashboard, bolalar xavfsizligi, kunlik 20 daqiqalik xavfsiz limit."
        )

    await message.answer(info_text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")

# 🔢 Matematika Olami tugmasi (ko'p tilli)
@router.message(F.text.in_([
    "🔢 Matematika Olami", "🔢 Мир Математики", "🔢 World of Math",
    "Matematika", "Математика", "Math", "matematika"
]))
async def math_menu_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if lang == "ru":
        text = (
            "🔢 <b>Мир Математики — Добро пожаловать на планету Сатурн!</b> 🪐\n\n"
            "Здесь мы решаем любые примеры и изучаем математику от 0 до 100%:\n"
            "• Сложение и вычитание: <code>25 + 35</code>, <code>17 - 5</code>\n"
            "• Умножение и деление: <code>12 * 8</code>, <code>100 / 4</code>\n"
            "• Квадраты, кубы и корни: <code>25 kvadrati</code>, <code>ildiz 144</code>\n"
            "• Секреты быстрого счета: <i>'Умножение на 11'</i>\n\n"
            "Напишите любой пример или отправьте голосовое сообщение! Я всё решу и объясню! 🚀✨"
        )
        voice_text = "Добро пожаловать в мир математики! Задай мне любой пример или попроси провести урок — я решу и объясню!"
    elif lang == "en":
        text = (
            "🔢 <b>World of Math — Welcome to Planet Saturn!</b> 🪐\n\n"
            "Here you can solve any math problems and learn from 0 to 100%:\n"
            "• Addition & Subtraction: <code>25 + 35</code>, <code>17 - 5</code>\n"
            "• Multiplication & Division: <code>12 * 8</code>, <code>100 / 4</code>\n"
            "• Squares, cubes, and roots: <code>square 25</code>, <code>sqrt 144</code>\n"
            "• Mental math tricks: <i>'Multiply by 11'</i>\n\n"
            "Send me any equation or voice message, and I'll solve it step-by-step! 🚀✨"
        )
        voice_text = "Welcome to the world of math! Ask me any problem or ask for a lesson, and I will solve it right away!"
    else:
        text = (
            "🔢 <b>Matematika Olami — Saturn Sayyorasiga Xush Kelibsiz!</b> 🪐\n\n"
            "Bu yerda siz har qanday misollarni yechishingiz va 0 dan 100 gacha dars olishingiz mumkin:\n"
            "• Qo'shish va ayirish: <code>25 + 35</code>, <code>17 - 5</code>\n"
            "• Ko'paytirish va bo'lish: <code>12 * 8</code>, <code>100 / 4</code>\n"
            "• Kvadrat, kub va ildizlar: <code>25 kvadrati</code>, <code>ildiz 144</code>\n"
            "• Tez hisoblash sirlari: <i>'11 ga tez ko'paytirish'</i>\n\n"
            "Menga istalgan misolingizni yozing yoki ovozli xabar qilib yuboring! Qadamma-qadam tushuntirib beraman! 🚀✨"
        )
        voice_text = "Matematika olamiga xush kelibsiz! Menga istalgan misolingizni ayting yoki dars o'tishimni so'rang, darhol tushuntirib beraman!"

    await message.answer(text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")
    asyncio.create_task(_async_send_voice_note(message, voice_text, user_id, lang=lang))

# 🇬🇧 Ingliz Tili tugmasi (ko'p tilli)
@router.message(F.text.in_([
    "🇬🇧 Ingliz Tili", "🇬🇧 Английский Язык", "🇬🇧 English Language",
    "Ingliz tili", "Английский", "English", "ingliz tili"
]))
async def english_menu_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if lang == "ru":
        text = (
            "🇬🇧 <b>Английский Язык — Добро пожаловать на планету Уран!</b> 🔵\n\n"
            "Изучаем английский весело и с правильным произношением:\n"
            "• <b>Числа:</b> от 0 до 100 (например: <code>100 на английском</code>)\n"
            "• <b>Слова:</b> <code>яблоко на английском</code>, <code>книга</code>, <code>школа</code>\n"
            "• <b>Произношение:</b> Голосовое прослушивание и тренировка речи!\n\n"
            "Напишите слово или нажмите <b>'🎙️ Детский Чат (Mini App)'</b> для интерактивной практики! 🌟"
        )
        voice_text = "Добро пожаловать на уроки английского! Спроси любое слово, и я научу правильному произношению!"
    elif lang == "en":
        text = (
            "🇬🇧 <b>English Language — Welcome to Planet Uranus!</b> 🔵\n\n"
            "Here we master English speaking, vocabulary, and correct pronunciation:\n"
            "• <b>Numbers:</b> from 0 to 100 (e.g. <code>Count to 10</code>)\n"
            "• <b>Vocabulary:</b> <code>apple</code>, <code>book</code>, <code>galaxy</code>\n"
            "• <b>Speaking:</b> Voice practice and conversations!\n\n"
            "Ask any question or tap <b>'🎙️ Kids Chat (Mini App)'</b> for live voice conversation! 🌟"
        )
        voice_text = "Welcome to our English learning world! Let's talk, learn new words, and have fun!"
    else:
        text = (
            "🇬🇧 <b>Ingliz Tili — Uran Sayyorasiga Xush Kelibsiz!</b> 🔵\n\n"
            "Bu yerda ingliz tilini qiziqarli o'rganamiz:\n"
            "• <b>Sonlar:</b> 0 dan 100 gacha (Masalan: <code>100 inglizcha</code>)\n"
            "• <b>So'zlar:</b> <code>olma inglizcha nima</code>, <code>kitob</code>, <code>maktab</code>\n"
            "• <b>Talaffuz:</b> Sof Amerika talaffuzida eshitish va mashq qilish!\n\n"
            "Jonli suhbatlashish uchun pastdagi <b>'🎙️ Kichikalloma Suhbat'</b> tugmasini bosing! 🌟"
        )
        voice_text = "Ingliz tili saboqlariga xush kelibsiz! Xohlagan so'zingizni so'rang, Amerika talaffuzi bilan o'rgataman!"

    await message.answer(text, reply_markup=get_main_keyboard(lang), parse_mode="HTML")
    asyncio.create_task(_async_send_voice_note(message, voice_text, user_id, lang=lang))

# 🪐 8 ta Sayyora tugmasi va buyruqlari
from planets_service import get_all_planets, get_planet_by_id, resolve_planet_image
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile

def get_planets_buttons() -> InlineKeyboardMarkup:
    planets = get_all_planets()
    emojis = {
        "Yer": "🌍", "Mars": "🔴", "Uran": "🔵", "Venera": "🟡",
        "Neptun": "🌊", "Saturn": "🪐", "Merkuriy": "🟣", "Yupiter": "🟠"
    }
    keyboard = []
    row = []
    for p in planets:
        t = p.get("title", "Sayyora")
        emo = emojis.get(t, "🪐")
        p_id = p.get("id")
        row.append(InlineKeyboardButton(text=f"{emo} {t}", callback_data=f"planet_view:{p_id}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@router.message(Command("sayyoralar"))
@router.message(F.text.in_([
    "🪐 8 ta Sayyora", "🪐 8 Планет", "🪐 8 Planets",
    "sayyoralar", "планеты", "planets"
]))
async def planets_menu_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    
    if lang == "ru":
        text = (
            "🪐 <b>Kichik Alloma — 8 Удивительных Планет!</b> 🚀✨\n\n"
            "В нашей экосистеме каждая планета — это отдельный мир знаний и развития:\n\n"
            "• 🌍 <b>Земля</b> — Когнитивное обучение (AI Учитель)\n"
            "• 🔴 <b>Марс</b> — Физическая активность и упражнения\n"
            "• 🔵 <b>Уран</b> — Английский язык и новые слова\n"
            "• 🟡 <b>Венера</b> — Золотые монеты и виртуальный магазин\n"
            "• 🌊 <b>Нептун</b> — Эмоциональная грамотность\n"
            "• 🪐 <b>Сатурн</b> — Математика и логика\n"
            "• 🟣 <b>Меркурий</b> — Профессии будущего и творчество\n"
            "• 🟠 <b>Юпитер</b> — Тайм-менеджмент и дисциплина\n\n"
            "📸 <b>Выберите планету ниже, чтобы увидеть её фото и подробности:</b> 👇"
        )
        voice_text = "Добро пожаловать в космическую систему Kichik Alloma! Выбери любую планету ниже, чтобы узнать её тайны!"
    elif lang == "en":
        text = (
            "🪐 <b>Kichik Alloma — 8 Incredible Planets!</b> 🚀✨\n\n"
            "In our ecosystem, each planet represents a unique world of growth:\n\n"
            "• 🌍 <b>Earth</b> — Cognitive Learning (AI Tutor)\n"
            "• 🔴 <b>Mars</b> — Physical fitness and workouts\n"
            "• 🔵 <b>Uranus</b> — English Language and Vocabulary\n"
            "• 🟡 <b>Venus</b> — Gold Coins & Virtual Store\n"
            "• 🌊 <b>Neptune</b> — Emotional Intelligence\n"
            "• 🪐 <b>Saturn</b> — Mathematics and Logic\n"
            "• 🟣 <b>Mercury</b> — Future Careers and Arts\n"
            "• 🟠 <b>Jupiter</b> — Time management & routines\n\n"
            "📸 <b>Select a planet below to see its picture and facts:</b> 👇"
        )
        voice_text = "Welcome to the Kichik Alloma universe! Pick any planet below to explore its mysteries and pictures!"
    else:
        text = (
            "🪐 <b>Kichik Alloma — 8 ta Moʻjizaviy Sayyora!</b> 🚀✨\n\n"
            "Platformamizda har bir sayyora bolalar uchun alohida rivojlanish va bilim olamidir:\n\n"
            "• 🌍 <b>Yer</b> — Kognitiv ta'lim (AI ustoz bilan darslar)\n"
            "• 🔴 <b>Mars</b> — Jismoniy faollik va mashqlar\n"
            "• 🔵 <b>Uran</b> — Ingliz tili va yangi so'zlar\n"
            "• 🟡 <b>Venera</b> — Oltin tangalar va virtual do'kon\n"
            "• 🌊 <b>Neptun</b> — Emotsional savodxonlik\n"
            "• 🪐 <b>Saturn</b> — Matematika va mantiq\n"
            "• 🟣 <b>Merkuriy</b> — Kelajak kasblari va ijodiyot\n"
            "• 🟠 <b>Yupiter</b> — Taym-menejment va intizom\n\n"
            "📸 <b>Sayyoraning rasmi va batafsil ma'lumotini ko'rish uchun pastdagi tugmalardan birini tanlang:</b> 👇"
        )
        voice_text = "Kichik Alloma koinotiga xush kelibsiz! Sayyoralardan birini tanlang, men uning rasmi va sirlarini ochib beraman!"

    await message.answer(text, reply_markup=get_planets_buttons(), parse_mode="HTML")
    asyncio.create_task(_async_send_voice_note(message, voice_text, user_id, lang=lang))

# Bitta sayyoraning rasmi va ma'lumotini ko'rsatish callback
@router.callback_query(F.data.startswith("planet_view:"))
async def planet_view_callback(callback: CallbackQuery) -> None:
    planet_id = callback.data.split(":")[1]
    p = get_planet_by_id(planet_id)
    user_id = callback.from_user.id
    lang = get_user_lang(user_id)
    if not p:
        await callback.answer("Sayyora topilmadi!", show_alert=True)
        return

    await callback.answer(f"🪐 {p.get('title')} sayyorasi tanlandi!")

    title = p.get("title", "")
    desc = p.get("description", "")
    caption = f"🪐 <b>{title} Sayyorasi</b>\n\n{desc}\n\n<i>Boshqa sayyorani ko'rish uchun quyidagi tugmalardan birini bosing:</i> 👇"

    img_path_or_url = resolve_planet_image(p.get("image"))
    sent = False

    if img_path_or_url:
        try:
            if os.path.exists(img_path_or_url):
                photo = FSInputFile(img_path_or_url)
            else:
                photo = URLInputFile(img_path_or_url)
            await callback.message.answer_photo(
                photo=photo,
                caption=caption,
                reply_markup=get_planets_buttons(),
                parse_mode="HTML"
            )
            sent = True
        except Exception as e:
            logger.warning(f"Rasm yuborishda xato: {e}")

    if not sent:
        await callback.message.answer(
            caption,
            reply_markup=get_planets_buttons(),
            parse_mode="HTML"
        )

    asyncio.create_task(_async_send_voice_note(callback.message, f"{title} sayyorasiga xush kelibsiz! {desc}", user_id, lang=lang))

# Boshqa barcha erkin savol va xabarlar (AI orqali bir zumda javob va fon rejimida ovoz)
@router.message(F.text)
async def default_message_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    user_text = message.text.strip()
    user_text_lower = user_text.lower()

    if any(k in user_text_lower for k in ["startup", "loyiha", "shoxrux", "asoschi", "vikipediya", "founder"]):
        await startup_info_handler(message)
        return

    # Darhol "yozilmoqda..." ko'rsatish
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    # AI orqali javob olish (0 dan 100 gacha darslar, internet qidiruvi, matematika, koinot)
    ai_reply = None
    try:
        from gemini_ai import ask_gemini
        ai_reply = ask_gemini(user_text, lang=lang)
    except Exception as e:
        logger.warning(f"AI so'rovida xatolik: {e}")

    if not ai_reply:
        ai_reply = f"Salom! <b>Kichik Alloma</b> ovozli Mini Appiga kirish uchun <b>'{t['btn_chat']}'</b> tugmasini bosing! 🎙️✨"

    # 1. Matnli javobni DARHOL yuborish!
    await message.answer(
        ai_reply,
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )

    # 2. Fon rejimida tilga mos o'g'il bola ovozini yuborish
    asyncio.create_task(_async_send_voice_note(message, ai_reply, user_id, lang=lang))

# Ovozli xabarlar kelganda yoki /voice komandasi
@router.message(Command("voice"))
@router.message(Command("ovoz"))
@router.message(F.voice)
async def default_voice_handler(message: Message) -> None:
    user_id = message.from_user.id
    lang = get_user_lang(user_id)
    t = TEXTS.get(lang, TEXTS["uz"])
    
    # 1. Agar foydalanuvchi ovozli xabar yuborgan bo'lsa
    if message.voice:
        local_ogg = f"user_voice_{user_id}_{message.message_id}.ogg"
        try:
            from elevenlabs_service import transcribe_voice
            from gemini_ai import ask_gemini

            await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

            # Telegramdan ovoz faylini yuklab olish
            file_info = await message.bot.get_file(message.voice.file_id)
            await message.bot.download_file(file_info.file_path, local_ogg)

            # Tilga mos STT orqali tinglash
            user_spoken_text = await asyncio.to_thread(transcribe_voice, local_ogg, lang)

            if os.path.exists(local_ogg):
                try: os.remove(local_ogg)
                except Exception: pass

            if user_spoken_text and len(user_spoken_text.strip()) > 1:
                ai_reply = ask_gemini(user_spoken_text, lang=lang)

                heard_label = "👂 <b>Sizni eshitdim:</b>" if lang == "uz" else ("👂 <b>Я услышал:</b>" if lang == "ru" else "👂 <b>I heard:</b>")
                reply_caption = f"{heard_label} <i>\"{user_spoken_text}\"</i>\n\n{ai_reply}"

                await message.answer(
                    reply_caption,
                    reply_markup=get_main_keyboard(lang),
                    parse_mode="HTML"
                )
                asyncio.create_task(_async_send_voice_note(message, ai_reply, user_id, lang=lang))
                return

        except Exception as err:
            logger.warning(f"Ovozli xabarni qayta ishlashda xatolik: {err}")
            if os.path.exists(local_ogg):
                try: os.remove(local_ogg)
                except Exception: pass

    # 2. Agar /voice komandasi bo'lsa yoki ovoz eshitilmasa
    voice_text = "Salom, kichik allomam! Menga xohlagan savolingizni ovozli xabar orqali yuboring, darhol o'g'il bola ovozida javob beraman!" if lang == "uz" else ("Привет, друг! Отправь мне голосовое сообщение, и я отвечу приятным голосом!" if lang == "ru" else "Hello friend! Send me a voice message and I'll reply with a friendly boy voice!")
    await message.answer(
        f"🎙️ <b>Kichik Alloma AI:</b>\n\n{voice_text}\n\nMini App: <b>'{t['btn_chat']}'</b> 🌟",
        reply_markup=get_main_keyboard(lang),
        parse_mode="HTML"
    )
    asyncio.create_task(_async_send_voice_note(message, voice_text, user_id, lang=lang))
