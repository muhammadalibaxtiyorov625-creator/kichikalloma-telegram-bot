# -*- coding: utf-8 -*-
import os
import json
import urllib.request
import logging

logger = logging.getLogger(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

FALLBACK_PLANETS = [
    {
        "id": 185,
        "title": "Yer",
        "title_ru": "Земля",
        "title_en": "Earth",
        "emoji": "🌍",
        "description": "🌍 <b>Yer Sayyorasi (Kognitiv ta'lim):</b>\nAI-ustoz bilan mustaqil fikrlash, fan va tabiat mo'jizalarini o'rganish makoni! Kunlik 20 daqiqalik xavfsiz qiziqarli darslar.",
        "description_ru": "🌍 <b>Планета Земля (Когнитивное развитие):</b>\nAI-наставник для развития логики, критического мышления и открытий! Безопасные 20-минутные интерактивные уроки.",
        "description_en": "🌍 <b>Planet Earth (Cognitive Learning):</b>\nSocratic AI tutor to develop critical thinking, curiosity, and scientific discovery! Safe 20-minute daily sessions.",
        "image": "images/uploads/640cb87ab57947c1877bf8d0a255db2d.png"
    },
    {
        "id": 186,
        "title": "Mars",
        "title_ru": "Марс",
        "title_en": "Mars",
        "emoji": "🔴",
        "description": "🔴 <b>Mars Sayyorasi (Jismoniy faollik):</b>\nQizil sayyora! Video asosida chaqqonlik, badantarbiya, quvvat va harakatli mashqlar maydoni.",
        "description_ru": "🔴 <b>Планета Марс (Физическая активность):</b>\nКрасная планета энергии и движения! Видео-зарядка, спорт, координация и бодрость каждый день.",
        "description_en": "🔴 <b>Planet Mars (Physical Fitness):</b>\nDynamic red planet! Video-guided workouts, agility, morning exercises, and healthy movement habits.",
        "image": "images/uploads/667e975600ac4c4ea7ab1b7346f54fef.png"
    },
    {
        "id": 187,
        "title": "Uran",
        "title_ru": "Уран",
        "title_en": "Uranus",
        "emoji": "🔵",
        "description": "🔵 <b>Uran Sayyorasi (Ingliz tili):</b>\nYangi so'zlar, to'g'ri Amerika talaffuzi, dialoglar va qiziqarli audio darslar orqali til o'rganish sayyorasi!",
        "description_ru": "🔵 <b>Планета Уран (Английский язык):</b>\nНовые слова, американское произношение, живые диалоги и интерактивная аудио-практика!",
        "description_en": "🔵 <b>Planet Uranus (English Language):</b>\nEnglish vocabulary, native American pronunciation, interactive dialogues, and fun voice speaking practice!",
        "image": "images/uploads/e891a5826f9348c0bd304bdcc1743fc3.png"
    },
    {
        "id": 188,
        "title": "Venera",
        "title_ru": "Венера",
        "title_en": "Venus",
        "emoji": "🟡",
        "description": "🟡 <b>Venera Sayyorasi (Virtual do'kon):</b>\nO'rganilgan bilimlar va yutuqlar evaziga berilgan 'Gold Coin' oltin tangalari orqali xaridlar maydoni!",
        "description_ru": "🟡 <b>Планета Венера (Виртуальный магазин):</b>\nМагазин наград! Дети обменивают заработанные золотые монеты (Gold Coins) на призы и костюмы для аватаров.",
        "description_en": "🟡 <b>Planet Venus (Virtual Store):</b>\nReward and motivation arena! Children use their earned Gold Coins to get badges, clothes, and special items.",
        "image": "images/uploads/ee368c1d41c942eabee5fc4fb65d20f2.png"
    },
    {
        "id": 189,
        "title": "Neptun",
        "title_ru": "Нептун",
        "title_en": "Neptune",
        "emoji": "🌊",
        "description": "🌊 <b>Neptun Sayyorasi (Emotsional savodxonlik):</b>\nHissiyotlarni tanish, xotirjamlik, yaxshi kayfiyat daraxti, mehr-oqibat va odob-axloq makoni.",
        "description_ru": "🌊 <b>Планета Нептун (Эмоциональный интеллект):</b>\nПонимание чувств, управление эмоциями, доброта, спокойствие и дерево хорошего настроения.",
        "description_en": "🌊 <b>Planet Neptune (Emotional Intelligence):</b>\nRecognizing emotions, calmness, empathy, kindness, mindfulness, and healthy communication.",
        "image": "images/uploads/8819bb07b5cf428d9cbf97848582d60c.png"
    },
    {
        "id": 190,
        "title": "Saturn",
        "title_ru": "Сатурн",
        "title_en": "Saturn",
        "emoji": "🪐",
        "description": "🪐 <b>Saturn Sayyorasi (Matematika va mantiq):</b>\nQiziqarli hisob-kitoblar, mantiqiy misollar, daraja va amallar, tezkor hisoblash sirlari olami!",
        "description_ru": "🪐 <b>Планета Сатурн (Математика и логика):</b>\nУстный быстрый счет, логические задачи, таблица умножения, квадраты чисел и математические ребусы!",
        "description_en": "🪐 <b>Planet Saturn (Mathematics & Logic):</b>\nMental math tricks, equations, multiplication, square numbers, and engaging logical puzzles from 0 to 100%!",
        "image": "images/uploads/e7173b3e04b949259e395de91f44f483.png"
    },
    {
        "id": 191,
        "title": "Merkuriy",
        "title_ru": "Меркурий",
        "title_en": "Mercury",
        "emoji": "🟣",
        "description": "🟣 <b>Merkuriy Sayyorasi (Kelajak kasblari):</b>\nShifokor, kosmonavt, dasturchi, olim, rassom kabi zamonaviy kasblar va ijodiyot sirlari.",
        "description_ru": "🟣 <b>Планета Меркурий (Профессии будущего):</b>\nКосмонавты, врачи, программисты, ученые, дизайнеры — знакомство с профессиями и развитие творчества.",
        "description_en": "🟣 <b>Planet Mercury (Future Careers & Arts):</b>\nAstronauts, doctors, software engineers, scientists, artists — exploring future careers and creative passions.",
        "image": "images/uploads/fc4ef45b85ae42b08eeec25ff0123931.png"
    },
    {
        "id": 192,
        "title": "Yupiter",
        "title_ru": "Юпитер",
        "title_en": "Jupiter",
        "emoji": "🟠",
        "description": "🟠 <b>Yupiter Sayyorasi (Taym-menejment):</b>\nKunni rejalashtirish, vaqt qadriga yetish, 25 daqiqa intizom qoidasi va maqsadlarga erishish mahorati.",
        "description_ru": "🟠 <b>Планета Юпитер (Тайм-менеджмент):</b>\nРаспорядок дня, ценность времени, концентрация внимания, правило 25 минут и развитие самодисциплины.",
        "description_en": "🟠 <b>Planet Jupiter (Time Management):</b>\nDaily routine planning, valuing time, focus and discipline habits, and the 25-minute Pomodoro method.",
        "image": "images/uploads/27eb77a596a74482b15a4ec56d3881e9.png"
    }
]

def get_all_planets(lang: str = "uz") -> list:
    """API dan yoki lokal bazadan sayyoralar ro'yxatini olish (tilga moslashtirilgan)"""
    planets = FALLBACK_PLANETS
    for api_url in ["http://127.0.0.1:3000/api/planets", "https://api.kichikalloma.uz/api/planets"]:
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "KichikAllomaBot/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data and len(data) >= 8:
                        pass
        except Exception:
            pass

    result = []
    for p in planets:
        item = dict(p)
        if lang == "ru":
            item["title"] = p.get("title_ru", p.get("title"))
            item["description"] = p.get("description_ru", p.get("description"))
        elif lang == "en":
            item["title"] = p.get("title_en", p.get("title"))
            item["description"] = p.get("description_en", p.get("description"))
        result.append(item)
    return result

def get_planet_by_id(planet_id: int, lang: str = "uz"):
    planets = get_all_planets(lang=lang)
    for p in planets:
        if str(p.get("id")) == str(planet_id):
            return p
    return None

def resolve_planet_image(img_raw: str) -> str:
    """Rasm faylini diskdan yoki URLdan topish"""
    if not img_raw:
        return None
    clean_name = os.path.basename(img_raw)
    
    # 1. tekegram/images/uploads ichida bormi?
    local_in_bot = os.path.join(CURRENT_DIR, "images", "uploads", clean_name)
    if os.path.exists(local_in_bot):
        return local_in_bot

    # 2. public/images/uploads ichida bormi?
    parent_pub = os.path.join(os.path.dirname(CURRENT_DIR), "public", "images", "uploads", clean_name)
    if os.path.exists(parent_pub):
        return parent_pub

    # 3. Agar URL bo'lsa
    if img_raw.startswith("http"):
        return img_raw
    return f"https://kichikalloma.uz/images/uploads/{clean_name}"

def get_overview_image(lang: str = "uz") -> str:
    """8 ta sayyora umumiy rasmini qaytarish"""
    if lang == "ru":
        target = "all_planets_ru.png"
    elif lang == "en":
        target = "all_planets_en.png"
    else:
        target = "all_planets.png"

    local_path = os.path.join(CURRENT_DIR, "images", "uploads", target)
    if os.path.exists(local_path):
        return local_path
    
    parent_path = os.path.join(os.path.dirname(CURRENT_DIR), "public", "images", "uploads", target)
    if os.path.exists(parent_path):
        return parent_path

    default_path = os.path.join(CURRENT_DIR, "images", "uploads", "all_planets.png")
    if os.path.exists(default_path):
        return default_path

    return f"https://kichikalloma.uz/images/uploads/{target}"
