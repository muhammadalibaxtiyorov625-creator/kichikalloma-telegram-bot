# Foydalanuvchi sozlamalari (vaqtinchalik xotira)
user_settings = {}

def get_user_lang(user_id: int) -> str:
    return user_settings.get(user_id, {}).get("lang", "uz")

def get_user_age(user_id: int) -> str:
    return user_settings.get(user_id, {}).get("age", "7-8")

def set_user_setting(user_id: int, key: str, value: str) -> None:
    if user_id not in user_settings:
        user_settings[user_id] = {"lang": "uz", "age": "7-8"}
    user_settings[user_id][key] = value

TEXTS = {
    "uz": {
        "welcome": (
            "Assalomu alaykum, <b>{name}</b>! 🌟\n\n"
            "Men <b>Kichik Alloma</b> — 7–11 yoshdagi bolalar va ota-onalar uchun "
            "AI asosidagi <b>8 Sayyorali Rivojlanish Ekotizimi</b>ning aqlli yordamchisiman! 🚀🪐\n\n"
            "🪐 <b>8 Ta Sayyora Ekotizimi:</b>\n"
            "• 🌍 <b>Yer:</b> Kognitiv ta’lim va AI Tutor (Sokratik usulda ta'lim)\n"
            "• 🟠 <b>Yupiter:</b> O‘z-o‘zini boshqarish, rejalashtirish va intizom\n"
            "• 🟡 <b>Venera:</b> Virtual Store (Gold Coin evaziga do'kon)\n"
            "• 🪐 <b>Saturn:</b> Matematika va mantiqiy misollar\n"
            "• 🟣 <b>Merkuriy:</b> Ijodkorlik va kasblar olami\n"
            "• 🔵 <b>Uran:</b> English Vocabulary (Inglizcha so'z boyligi)\n"
            "• 🔴 <b>Mars:</b> Jismoniy faollik va sport mashqlari\n"
            "• 🌊 <b>Neptun:</b> Emotsional savodxonlik va his-tuyg'ular\n\n"
            "🛡️ <b>Xavfsizlik:</b> Parent Dashboard, kunlik 20 daqiqa xavfsiz AI limiti\n"
            "👨‍💻 <b>Asoschi:</b> Shoxrux Komiljonov va uning iqtidorli jamoasi\n"
            "🌐 <b>Veb-sayt:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
            "📖 <b>Vikipediya:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Loyiha maqolasi</a>\n\n"
            "Pastdagi bo'limlardan birini tanlang yoki savolingizni yozing / ovozli yuboring! 👇"
        ),
        "btn_chat": "🎙️ Kichikalloma Suhbat (Mini App)",
        "btn_math": "🔢 Matematika Olami",
        "btn_english": "🇬🇧 Ingliz Tili",
        "btn_planets": "🪐 8 ta Sayyora",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_help": "🆘 Yordam (/help)",
        "btn_close": "🔙 Yopish",
        "input_placeholder": "Savol yozing yoki bo'limni tanlang...",
        "lang_changed_msg": (
            "🇺🇿 <b>O'zbek tili muvaffaqiyatli tanlandi!</b>\n\n"
            "Barcha bo'limlar, darslar va ovozli javoblar o'zbek tiliga o'tkazildi! 🌟"
        ),
        "help_intro": (
            "✍️ <b>Muammo yoki savolingizni pastga yozing:</b>\n\n"
            "Pastdagi matn yozish joyiga xabaringizni yozib, <b>yuborish (jo'natish)</b> tugmasini bosing.\n\n"
            "Xabaringiz yuborilgach, adminimiz 24 soat ichida sizga javob yozadi.\n"
            "<i>(Bekor qilish uchun pastdagi '❌ Bekor qilish' tugmasini bosing)</i>"
        ),
        "help_sent": (
            "✅ <b>Xabaringiz qabul qilindi!</b>\n\n"
            "Sizga <b>24 soatning ichida admin javob yozadi</b>! ✨"
        ),
        "settings_title": (
            "⚙️ <b>Sozlamalar bo'limi:</b>\n\n"
            "Quyidagi tugmalardan o'zingizga qulay <b>tilni tanlang</b>:"
        ),
        "cancel": "❌ Bekor qilish"
    },
    "ru": {
        "welcome": (
            "Привет, <b>{name}</b>! 🌟\n\n"
            "Я <b>Kichikalloma Ai</b> — умный и добрый друг для детей 7–11 лет и их родителей! 🤖✨\n\n"
            "📚 <b>Чему я обучаю:</b>\n"
            "• 🪐 <b>8 планет:</b> Солнечная система и тайны космоса\n"
            "• 🇬🇧 <b>Английский язык:</b> Разговорная речь, словарный запас и произношение\n"
            "• 🔢 <b>Математика:</b> Веселый счет, логика и быстрое умножение\n"
            "• 🌸 <b>Воспитание:</b> Вежливость, этикет и доброта\n"
            "• 🗣️ <b>Голосовое общение:</b> Развитие речи и мышления ребенка\n\n"
            "👨‍💻 <b>Основатель:</b> Шохрух Комилджонов и его команда\n"
            "🌐 <b>Сайт:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n\n"
            "Выберите раздел внизу или задайте вопрос голосом / текстом! 👇"
        ),
        "btn_chat": "🎙️ Детский Чат (Mini App)",
        "btn_math": "🔢 Мир Математики",
        "btn_english": "🇬🇧 Английский Язык",
        "btn_planets": "🪐 8 Планет",
        "btn_settings": "⚙️ Настройки",
        "btn_help": "🆘 Помощь (/help)",
        "btn_close": "🔙 Закрыть",
        "input_placeholder": "Задайте вопрос или выберите раздел...",
        "lang_changed_msg": (
            "🇷🇺 <b>Русский язык успешно выбран!</b>\n\n"
            "Все кнопки, уроки и голосовые ответы теперь на русском языке! 🌟"
        ),
        "help_intro": (
            "✍️ <b>Напишите ваш вопрос или проблему внизу:</b>\n\n"
            "Введите текст в поле ввода внизу и нажмите <b>Отправить</b>.\n\n"
            "Администратор ответит вам в течение 24 часов.\n"
            "<i>(Для отмены нажмите '❌ Отмена' внизу)</i>"
        ),
        "help_sent": (
            "✅ <b>Ваше сообщение принято!</b>\n\n"
            "Администратор <b>ответит вам в течение 24 часов</b>! ✨"
        ),
        "settings_title": (
            "⚙️ <b>Настройки языка:</b>\n\n"
            "Выберите удобный для вас <b>язык интерфейса</b>:"
        ),
        "cancel": "❌ Отмена"
    },
    "en": {
        "welcome": (
            "Hello, <b>{name}</b>! 🌟\n\n"
            "I am <b>Kichikalloma Ai</b> — a smart, friendly AI companion for kids aged 7 to 11 and their parents! 🤖✨\n\n"
            "📚 <b>What I teach:</b>\n"
            "• 🪐 <b>8 Planets:</b> The Solar System and mysteries of space\n"
            "• 🇬🇧 <b>English Language:</b> Daily speaking, vocabulary, and pronunciation\n"
            "• 🔢 <b>Mathematics:</b> Fun counting, mental math, and logic\n"
            "• 🌸 <b>Etiquette & Values:</b> Kindness, manners, and discipline\n"
            "• 🗣️ <b>Voice Chat:</b> Speaking and critical thinking skills\n\n"
            "👨‍💻 <b>Founder:</b> Shoxrux Komiljonov and his team\n"
            "🌐 <b>Website:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n\n"
            "Choose an option below or ask any question by voice or text! 👇"
        ),
        "btn_chat": "🎙️ Kids Chat (Mini App)",
        "btn_math": "🔢 World of Math",
        "btn_english": "🇬🇧 English Language",
        "btn_planets": "🪐 8 Planets",
        "btn_settings": "⚙️ Settings",
        "btn_help": "🆘 Help (/help)",
        "btn_close": "🔙 Close",
        "input_placeholder": "Ask a question or select a topic...",
        "lang_changed_msg": (
            "🇬🇧 <b>English language successfully selected!</b>\n\n"
            "All menu buttons, lessons, and voice responses are now in English! 🌟"
        ),
        "help_intro": (
            "✍️ <b>Type your message or question below:</b>\n\n"
            "Type into the message input field and press <b>Send</b>.\n\n"
            "Our admin will reply to you within 24 hours.\n"
            "<i>(To cancel, tap '❌ Cancel' below)</i>"
        ),
        "help_sent": (
            "✅ <b>Your message has been received!</b>\n\n"
            "Our admin <b>will reply to you within 24 hours</b>! ✨"
        ),
        "settings_title": (
            "⚙️ <b>Language Settings:</b>\n\n"
            "Select your preferred <b>interface language</b>:"
        ),
        "cancel": "❌ Cancel"
    }
}
