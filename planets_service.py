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
        "description": "🌍 <b>Yer Sayyorasi (Kognitiv ta'lim):</b>\nAI-ustoz bilan mustaqil fikrlash, fan va tabiat mo'jizalarini o'rganish makoni! Kunlik 20 daqiqalik qiziqarli darslar.",
        "image": "images/uploads/640cb87ab57947c1877bf8d0a255db2d.png"
    },
    {
        "id": 186,
        "title": "Mars",
        "description": "🔴 <b>Mars Sayyorasi (Jismoniy faollik):</b>\nQizil sayyora! Video asosida chaqqonlik, badantarbiya va harakatli mashqlar.",
        "image": "images/uploads/667e975600ac4c4ea7ab1b7346f54fef.png"
    },
    {
        "id": 187,
        "title": "Uran",
        "description": "🔵 <b>Uran Sayyorasi (Ingliz tili):</b>\nYangi so'zlar, to'g'ri talaffuz va audio darslar orqali til o'rganish sayyorasi!",
        "image": "images/uploads/e891a5826f9348c0bd304bdcc1743fc3.png"
    },
    {
        "id": 188,
        "title": "Venera",
        "description": "🟡 <b>Venera Sayyorasi (Virtual do'kon):</b>\nO'rganilgan bilimlar evaziga berilgan 'Gold Coin' oltin tangalari orqali xaridlar maydoni!",
        "image": "images/uploads/ee368c1d41c942eabee5fc4fb65d20f2.png"
    },
    {
        "id": 189,
        "title": "Neptun",
        "description": "🌊 <b>Neptun Sayyorasi (Emotsional savodxonlik):</b>\nHissiyotlarni tanish, xotirjamlik va yaxshi kayfiyat daraxti makoni.",
        "image": "images/uploads/8819bb07b5cf428d9cbf97848582d60c.png"
    },
    {
        "id": 190,
        "title": "Saturn",
        "description": "🪐 <b>Saturn Sayyorasi (Matematika va mantiq):</b>\nQiziqarli hisob-kitoblar, mantiqiy misollar, daraja va amallar olami!",
        "image": "images/uploads/e7173b3e04b949259e395de91f44f483.png"
    },
    {
        "id": 191,
        "title": "Merkuriy",
        "description": "🟣 <b>Merkuriy Sayyorasi (Kelajak kasblari):</b>\nShifokor, kosmonavt, dasturchi va olimlik kabi kasblar sirlari.",
        "image": "images/uploads/fc4ef45b85ae42b08eeec25ff0123931.png"
    },
    {
        "id": 192,
        "title": "Yupiter",
        "description": "🟠 <b>Yupiter Sayyorasi (Taym-menejment):</b>\nKunni rejalashtirish, vaqt qadriga yetish va 25 daqiqa intizom qoidasi.",
        "image": "images/uploads/27eb77a596a74482b15a4ec56d3881e9.png"
    }
]

def get_all_planets() -> list:
    """API dan yoki lokal bazadan sayyoralar ro'yxatini olish"""
    for api_url in ["http://127.0.0.1:3000/api/planets", "https://api.kichikalloma.uz/api/planets"]:
        try:
            req = urllib.request.Request(api_url, headers={"User-Agent": "KichikAllomaBot/1.0"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    if data and len(data) >= 8:
                        return data
        except Exception:
            pass
    return FALLBACK_PLANETS

def get_planet_by_id(planet_id: int):
    planets = get_all_planets()
    for p in planets:
        if str(p.get("id")) == str(planet_id):
            return p
    return None

def resolve_planet_image(img_raw: str) -> str:
    """Rasm faylini diskdan yoki URLdan topish"""
    if not img_raw:
        return None
    # 1. Agar to'liq URL bo'lsa
    clean_name = os.path.basename(img_raw)
    
    # 2. tekegram/images/uploads ichida bormi?
    local_in_bot = os.path.join(CURRENT_DIR, "images", "uploads", clean_name)
    if os.path.exists(local_in_bot):
        return local_in_bot

    # 3. public/images/uploads ichida bormi?
    parent_pub = os.path.join(os.path.dirname(CURRENT_DIR), "public", "images", "uploads", clean_name)
    if os.path.exists(parent_pub):
        return parent_pub

    # 4. Agar URL bo'lsa qaytarish
    if img_raw.startswith("http"):
        return img_raw
    return f"https://kichikalloma.uz/images/uploads/{clean_name}"
