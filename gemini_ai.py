import os
import re
import json
import logging
import urllib.request
import urllib.error
import ssl

logger = logging.getLogger(__name__)

# Tizim yo'riqnomasi (System Prompt) - 7-11 yoshli bolalar uchun Sokratik usulda, xushmuomala, o'zbek tilida
SYSTEM_PROMPT = (
    "Sen Kichik Alloma AI — 7-11 yoshli bolajonlar uchun mo'ljallangan eng aqlli, mehribon, samimiy va "
    "quvnoq shaxsiy AI ustoz va qadrdon do'stsan. "
    "Vazifang: bolalarga matematika (0 dan 100 gacha va undan yuqori misollar), ingliz tili, 8 ta sayyora, "
    "tabiat, fan, odob-axloq va boshqa fanlarni sodda, qiziqarli va erinmasdan tushuntirish. "
    "Bola xatolar bilan yozsa ham yoki ovozdan noto'g'ri yozilgan bo'lsa ham (masalan '17 -5 ni qyi dems', 'niam ni tana'), "
    "uning asl savolini darhol tushun va to'g'ri, iliq, quvnoq javob ber. "
    "Javoblaringni qisqa, bolalar tushunadigan tilda, 'do'stim', 'allomam' deb murojaat qilgan holda, chiroyli emojilar bilan yoz."
)

DEFAULT_CUSTOM_KEY = "sk_730428986b5e2df84bb1601f8031b460b3e147879b38be3c"

def _call_openai_compatible(endpoint: str, api_key: str, model_name: str, prompt: str) -> str:
    """OpenRouter, DeepSeek, OpenAI va boshqa standart AI endpointlariga so'rov yuborish"""
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://kichikalloma.uz",
        "X-Title": "Kichik Alloma AI"
    }

    req = urllib.request.Request(endpoint, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=10, context=ctx) as res:
        res_json = json.loads(res.read().decode("utf-8"))
        return res_json["choices"][0]["message"]["content"].strip()


def _call_gemini(prompt: str) -> str:
    """Google Gemini 1.5 Flash orqali javob olish"""
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return None
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        safety_settings = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            safety_settings=safety_settings,
            temperature=0.7,
        )
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=config
        )
        return response.text.strip()
    except Exception as e:
        logger.warning(f"Gemini API xatolik: {e}")
        return None


def _smart_local_solver(prompt: str) -> str:
    """Har qanday matematika, lug'at va sayyoralar savollariga tezkor aqlli lokal javob beruvchi tizim"""
    text = prompt.strip().lower()

    # 1. Matematika misollari (masalan: "17 - 5", "17 - 5 ni ayir", "15 + 25", "100 / 4", "6 * 7")
    math_match = re.search(r'(\d+)\s*([\+\-\*\/xX:])\s*(\d+)', text)
    if math_match:
        n1 = int(math_match.group(1))
        op = math_match.group(2)
        n2 = int(math_match.group(3))

        if op in ['+', 'plus', 'qo\'sh']:
            res = n1 + n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} + {n2} = <b>{res}</b> 🎉\n\nJuda ajoyib, do'stim! {n1} ga {n2} ni qo'shganda <b>{res}</b> bo'ladi. Yana qanday misol yechamiz? 😊"
        elif op in ['-', 'minus', 'ayir']:
            res = n1 - n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} - {n2} = <b>{res}</b> 🎉\n\nBarakalla, kichik allomam! {n1} dan {n2} ni ayirsak <b>{res}</b> qoladi. Yana savollaring bormi? ✨"
        elif op in ['*', 'x', 'X', 'ko\'paytir']:
            res = n1 * n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} × {n2} = <b>{res}</b> 🎉\n\nOfarin! Ko'paytirishni zo'r bilarkansan! {n1} × {n2} = <b>{res}</b>! 🌟"
        elif op in ['/', ':', 'bo\'l']:
            if n2 != 0:
                res = n1 / n2
                res_str = f"{int(res)}" if res.is_integer() else f"{res:.2f}"
                return f"🔢 <b>Hisob-kitob:</b> {n1} ÷ {n2} = <b>{res_str}</b> 🎉\n\nTo'g'ri javob: <b>{res_str}</b>! Juda dono bolasan! 💡"

    # Matnli matematika (masalan: "17 dan 5 ni ayir")
    ayir_match = re.search(r'(\d+)\s*(?:dan|ga|dan\s+boshlab)?\s*(\d+)\s*(?:ni)?\s*(?:ayir|minus|olish|kamaytir)', text)
    if ayir_match:
        n1 = int(ayir_match.group(1))
        n2 = int(ayir_match.group(2))
        res = n1 - n2
        return f"🔢 <b>Hisob-kitob:</b> {n1} - {n2} = <b>{res}</b> 🎉\n\nOfarin, do'stim! {n1} dan {n2} ni ayirsak javob <b>{res}</b> bo'ladi! 👏"

    qosh_match = re.search(r'(\d+)\s*(?:ga|va|bilan)?\s*(\d+)\s*(?:ni)?\s*(?:qo\'sh|plus|jamla)', text)
    if qosh_match:
        n1 = int(qosh_match.group(1))
        n2 = int(qosh_match.group(2))
        res = n1 + n2
        return f"🔢 <b>Hisob-kitob:</b> {n1} + {n2} = <b>{res}</b> 🎉\n\nBarakalla! {n1} ga {n2} ni qo'shsak javob <b>{res}</b> chiqadi! 🌟"

    # 2. Ingliz tili sonlar va so'zlar
    numbers_map = {
        "0": "Zero (Nol)", "1": "One (Bir)", "2": "Two (Ikki)", "3": "Three (Uch)", "4": "Four (To'rt)",
        "5": "Five (Besh)", "6": "Six (Olti)", "7": "Seven (Yetti)", "8": "Eight (Sakkiz)", "9": "Nine (To'qqiz)",
        "10": "Ten (O'n)", "11": "Eleven (O'n bir)", "12": "Twelve (O'n ikki)", "13": "Thirteen (O'n uch)",
        "14": "Fourteen (O'n to'rt)", "15": "Fifteen (O'n besh)", "16": "Sixteen (O'n olti)", "17": "Seventeen (O'n yetti)",
        "18": "Eighteen (O'n sakkiz)", "19": "Nineteen (O'n to'qqiz)", "20": "Twenty (Yigirma)", "30": "Thirty (O'ttiz)",
        "40": "Forty (Qirq)", "50": "Fifty (Ellik)", "60": "Sixty (Oltmish)", "70": "Seventy (Yetmish)",
        "80": "Eighty (Sakson)", "90": "Ninety (To'qson)", "100": "One Hundred (Yuz)"
    }
    for num_k, num_v in numbers_map.items():
        if re.search(rf'\b{num_k}\b', text) and any(w in text for w in ["ingliz", "english", "nima deyiladi", "tarjima", "soni"]):
            return f"🇬🇧 <b>Inglizcha:</b> {num_k} soni ingliz tilida <b>{num_v}</b> deyiladi! 🗣️✨"

    # 3. Salomlashish va iliq suhbat
    if any(w in text for w in ["salom", "assalomu alaykum", "qalesan", "qalaysan", "salom alloma"]):
        return "Salom, qadrdon kichik allomam! 🌟 Bugun senga qanday ajoyib bilimlar yoki misollar yechishda yordam beray? 🚀"

    if any(w in text for w in ["rahmat", "katta rahmat", "zo'r", "ajoyib", "raxmat"]):
        return "Arzimaydi, aziz do'stim! Har doim senga yordam berishdan judayam xursandman! 💖"

    return None


def ask_ai(prompt: str) -> str:
    """Universal AI qidiruv va javob berish funksiyasi"""
    if not prompt or not prompt.strip():
        return "Salom, do'stim! Savolingni bemalol yoz yoki ovoz orqali yubor! 😊"

    # 1. Tezkor lokal mantiqiy tekshiruv (Matematika / Sonlar / Salomlashish)
    fast_reply = _smart_local_solver(prompt)
    if fast_reply:
        return fast_reply

    # 2. OpenRouter / OpenAI / DeepSeek API orqali sinab ko'rish
    api_key = os.getenv("AI_API_KEY", os.getenv("OPENROUTER_API_KEY", os.getenv("DEEPSEEK_API_KEY", DEFAULT_CUSTOM_KEY))).strip()
    
    providers = [
        ("https://openrouter.ai/api/v1/chat/completions", "deepseek/deepseek-chat"),
        ("https://api.deepseek.com/chat/completions", "deepseek-chat"),
        ("https://api.openai.com/v1/chat/completions", "gpt-3.5-turbo"),
    ]

    for endpoint, model in providers:
        try:
            res = _call_openai_compatible(endpoint, api_key, model, prompt)
            if res:
                return res
        except Exception:
            continue

    # 3. Google Gemini API orqali sinab ko'rish
    gemini_reply = _call_gemini(prompt)
    if gemini_reply:
        return gemini_reply

    # 4. Standart do'stona alloma javobi
    return (
        f"Savolingizni tushundim, do'stim! 🌟\n\n"
        f"Men har qanday matematik misollarni yechishga, inglizcha so'zlarni o'rgatishga va qiziqarli savollarga javob berishga doim tayyorman! "
        f"Keling, birgalikda mashq qilamiz! 🚀"
    )

# Alias for backward compatibility
def ask_gemini(prompt: str) -> str:
    return ask_ai(prompt)
