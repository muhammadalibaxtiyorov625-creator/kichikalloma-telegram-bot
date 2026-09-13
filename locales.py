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
            "• 🪐 <b>Merkuriy:</b> Ijodkorlik va kasblar olami\n"
            "• 🔵 <b>Uran:</b> English Vocabulary (Inglizcha so'z boyligi)\n"
            "• 🔴 <b>Mars:</b> Jismoniy faollik va sport mashqlari\n"
            "• 🌊 <b>Neptun:</b> Emotsional savodxonlik va his-tuyg'ular\n\n"
            "🛡️ <b>Xavfsizlik:</b> Parent Dashboard, kunlik 20 daqiqa xavfsiz AI limiti\n"
            "👨‍💻 <b>Asoschi:</b> Komiljonov Shoxruxbek Komiljon o'g'li\n"
            "🌐 <b>Veb-sayt:</b> <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
            "📖 <b>Vikipediya:</b> <a href='https://uz.wikipedia.org/w/index.php?title=Startup&oldid=6268714'>Loyiha maqolasi</a>\n\n"
            "Pastdagi <b>'🎙️ Kichikalloma Suhbat'</b> tugmasini bosing va bolangiz bilan o'rganishni boshlang!"
        ),
        "btn_chat": "🎙️ Kichikalloma Suhbat (Mini App)",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_help": "🆘 Yordam (/help)",
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
            "Tilni yoki bolaning yoshini tanlang:"
        ),
        "cancel": "❌ Bekor qilish"
    },
    "ru": {
        "welcome": (
            "Привет, <b>{name}</b>! 🌟\n\n"
            "Я <b>Kichikalloma Ai</b> — умный и добрый друг для детей 7–11 лет! 🤖✨\n\n"
            "📚 <b>Чему я обучаю:</b>\n"
            "• 🪐 <b>8 планет:</b> Солнечная система и тайны космоса\n"
            "• 🇬🇧 <b>Английский язык:</b> Разговорная речь и правильное произношение\n"
            "• 🔢 <b>Математика:</b> Веселый счет и логика\n"
            "• 🌸 <b>Воспитание:</b> Вежливость, этикет и доброта\n"
            "• 🗣️ <b>Голосовое общение:</b> Развитие речи и мышления ребенка\n\n"
            "Нажмите кнопку ниже и начните говорить!"
        ),
        "btn_chat": "🎙️ Детский Чат (Mini App)",
        "btn_settings": "⚙️ Настройки",
        "btn_help": "🆘 Помощь (/help)",
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
            "⚙️ <b>Настройки:</b>\n\n"
            "Выберите язык интерфейса или возраст ребенка:"
        ),
        "cancel": "❌ Отмена"
    },
    "en": {
        "welcome": (
            "Hello, <b>{name}</b>! 🌟\n\n"
            "I am <b>Kichikalloma Ai</b> — a smart, friendly AI companion for kids aged 7 to 11! 🤖✨\n\n"
            "📚 <b>What I teach:</b>\n"
            "• 🪐 <b>8 Planets:</b> The Solar System and mysteries of space\n"
            "• 🇬🇧 <b>English Language:</b> Daily speaking and correct pronunciation\n"
            "• 🔢 <b>Mathematics:</b> Fun counting and logic riddles\n"
            "• 🌸 <b>Etiquette & Values:</b> Kindness and good manners\n"
            "• 🗣️ <b>Voice Chat:</b> Speaking and critical thinking skills\n\n"
            "Press the button below to start talking!"
        ),
        "btn_chat": "🎙️ Voice Chat (Mini App)",
        "btn_settings": "⚙️ Settings",
        "btn_help": "🆘 Help (/help)",
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
            "⚙️ <b>Settings:</b>\n\n"
            "Select language or child's age group:"
        ),
        "cancel": "❌ Cancel"
    }
}
