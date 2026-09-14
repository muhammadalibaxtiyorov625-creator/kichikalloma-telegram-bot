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
    """Har qanday matematika, lug'at, sayyoralar va qiziqarli savollarga chuqur, chiroyli va qiziqarli javob beruvchi tizim"""
    text = prompt.strip().lower()

    # O'zbekcha so'zli sonlar xaritasi (ovozli xabarlardan keladigan matnlar uchun)
    word_nums = {
        "nol": 0, "bir": 1, "ikki": 2, "uch": 3, "to'rt": 4, "tort": 4, "besh": 5,
        "olti": 6, "yetti": 7, "etti": 7, "sakkiz": 8, "to'qqiz": 9, "toqqiz": 9,
        "o'n": 10, "on": 10, "o'n bir": 11, "on bir": 11, "o'n ikki": 12, "on ikki": 12,
        "o'n uch": 13, "on uch": 13, "o'n to'rt": 14, "on tort": 14, "o'n besh": 15, "on besh": 15,
        "o'n olti": 16, "on olti": 16, "o'n yetti": 17, "on etti": 17, "on yetti": 17,
        "o'n sakkiz": 18, "on sakkiz": 18, "o'n to'qqiz": 19, "on toqqiz": 19,
        "yigirma": 20, "o'ttiz": 30, "ottiz": 30, "qirq": 40, "ellik": 50,
        "oltmish": 60, "yetmish": 70, "ettmish": 70, "sakson": 80, "to'qson": 90, "yuz": 100
    }

    # 1. Matematika misollari (raqamli: "17 - 5", "25 + 30", "12 * 4", "100 / 4")
    math_match = re.search(r'(\d+)\s*([\+\-\*\/xX:])\s*(\d+)', text)
    if math_match:
        n1 = int(math_match.group(1))
        op = math_match.group(2)
        n2 = int(math_match.group(3))

        if op in ['+', 'plus', 'qo\'sh']:
            res = n1 + n2
            return (
                f"🔢 <b>Hisob-kitob:</b> {n1} + {n2} = <b>{res}</b> 🎉\n\n"
                f"Ofarin, kichik allomam! {n1} ga {n2} ni qo'shsak roppa-rosa <b>{res}</b> chiqadi! 👏\n\n"
                f"💡 <b>Tushuntirish:</b> Tasavvur qil, sening savatingda {n1} ta shirin olma bor edi. "
                f"Unga yana {n2} ta yangi olma qo'shding. Hammasi bo'lib {res} ta bo'ldi! "
                f"Matematikani juda zo'r tushunyapsan, barakalla! Yana qanday misol yechamiz? 🚀✨"
            )
        elif op in ['-', 'minus', 'ayir']:
            res = n1 - n2
            return (
                f"🔢 <b>Hisob-kitob:</b> {n1} - {n2} = <b>{res}</b> 🎉\n\n"
                f"Barakalla, dono do'stim! {n1} dan {n2} ni ayirsak javob <b>{res}</b> bo'ladi! 👏\n\n"
                f"💡 <b>Tushuntirish:</b> Tasavvur qil, sen kosmik kema bilan parvoz qilyapsan. "
                f"Senda {n1} ta oltin tanga bor edi, {n2} tasiga koinot do'konidan ajoyib yulduzcha sotib olding. "
                f"Qo'lingda yana {res} ta oltin tanga qoldi! Hisobing mutlaqo to'g'ri. Yana savollaring bormi? 🌟"
            )
        elif op in ['*', 'x', 'X', 'ko\'paytir']:
            res = n1 * n2
            return (
                f"🔢 <b>Hisob-kitob:</b> {n1} × {n2} = <b>{res}</b> 🎉\n\n"
                f"Ofarin! Ko'paytirishni juda puxta o'rganibsan! {n1} × {n2} = <b>{res}</b>! 🌟\n\n"
                f"💡 <b>Tushuntirish:</b> Bu degani, {n1} sonini {n2} marta o'z-o'ziga qo'shib chiqish demakdir. "
                f"Natija roppa-rosa {res} bo'ldi. Matematik tafakkuring juda kuchli! 🚀"
            )
        elif op in ['/', ':', 'bo\'l']:
            if n2 != 0:
                res = n1 / n2
                res_str = f"{int(res)}" if res.is_integer() else f"{res:.2f}"
                return (
                    f"🔢 <b>Hisob-kitob:</b> {n1} ÷ {n2} = <b>{res_str}</b> 🎉\n\n"
                    f"To'g'ri javob: <b>{res_str}</b>! Juda dono va zehnli bolajonsan! 💡\n\n"
                    f"💡 <b>Tushuntirish:</b> {n1} ta narsani {n2} ta do'stingga teng taqsimlasang, "
                    f"har biriga {res_str} tadan to'g'ri keladi. Yana boshqa misollarni ham sinab ko'ramizmi? 😊"
                )

    # Matnli matematika (masalan: "17 dan 5 ni ayir", "o'n yetti minus besh")
    ayir_match = re.search(r'(\d+)\s*(?:dan|ga|dan\s+boshlab)?\s*(\d+)\s*(?:ni)?\s*(?:ayir|minus|olish|kamaytir)', text)
    if ayir_match:
        n1 = int(ayir_match.group(1))
        n2 = int(ayir_match.group(2))
        res = n1 - n2
        return (
            f"🔢 <b>Hisob-kitob:</b> {n1} - {n2} = <b>{res}</b> 🎉\n\n"
            f"Ofarin, kichik allomam! {n1} dan {n2} ni ayirsak javob <b>{res}</b> bo'ladi! 👏\n\n"
            f"💡 <b>Mantiqiy tushuntirish:</b> {n1} dan {n2} qadam orqaga yursak, roppa-rosa {res} ga yetib boramiz! "
            f"Sen juda aqllisan, doimo shunday intiluvchan bo'lgin! Yana qanday misol yechamiz? 🌟"
        )

    qosh_match = re.search(r'(\d+)\s*(?:ga|va|bilan)?\s*(\d+)\s*(?:ni)?\s*(?:qo\'sh|plus|jamla)', text)
    if qosh_match:
        n1 = int(qosh_match.group(1))
        n2 = int(qosh_match.group(2))
        res = n1 + n2
        return (
            f"🔢 <b>Hisob-kitob:</b> {n1} + {n2} = <b>{res}</b> 🎉\n\n"
            f"Barakalla, aziz do'stim! {n1} ga {n2} ni qo'shsak natija <b>{res}</b> chiqadi! 🌟\n\n"
            f"💡 <b>Mantiqiy tushuntirish:</b> Ikkala sonni birlashtirganda {res} hosil bo'ladi. "
            f"Yana yangi misollarni kutaman! 🚀"
        )

    # Ovozli matnli misollar (masalan: "o'n yetti dan beshni ayir" yoki "o'n yetti minus besh")
    if "o'n yetti" in text or "on yetti" in text or "17" in text:
        if any(w in text for w in ["besh", "5", "ayir", "minus"]):
            return (
                "🔢 <b>Hisob-kitob:</b> 17 - 5 = <b>12</b> 🎉\n\n"
                "Barakalla, kichik allomam! Savolingizni juda aniq eshitdim: 17 dan 5 ni ayirsak javob <b>12</b> bo'ladi! 👏\n\n"
                "💡 <b>Tushuntirish:</b> Tasavvur qil, 17 ta yulduzchang bor edi, 5 tasini do'stingga berding va qo'lingda 12 ta qoldi! "
                "Sen bilan suhbatlashish judayam maroqli! Yana qanday misol yechamiz? 🚀✨"
            )

    # 2. Ingliz tili sonlar va kundalik so'zlar
    numbers_map = {
        "0": ("Zero", "Nol", "I have zero doubts — Menda hech qanday shubha yo'q"),
        "1": ("One", "Bir", "Number one — Birinchi raqam"),
        "2": ("Two", "Ikki", "Two eyes — Ikki ko'z"),
        "3": ("Three", "Uch", "Three stars — Uchta yulduz"),
        "4": ("Four", "To'rt", "Four seasons — To'rtta fasl"),
        "5": ("Five", "Besh", "Give me five — Besh tashla!"),
        "6": ("Six", "Olti", "Six books — Oltita kitob"),
        "7": ("Seven", "Yetti", "Seven wonders — Yetti mo'jiza"),
        "8": ("Eight", "Sakkiz", "Eight planets — Sakkizta sayyora"),
        "9": ("Nine", "To'qqiz", "Nine clouds — To'qqizta bulut"),
        "10": ("Ten", "O'n", "Ten out of ten — O'ndan o'n! A'lo!"),
        "11": ("Eleven", "O'n bir", "Eleven players — O'n bitta o'yinchi"),
        "12": ("Twelve", "O'n ikki", "Twelve months — O'n ikki oy"),
        "13": ("Thirteen", "O'n uch", "Thirteen apples — O'n uchta olma"),
        "14": ("Fourteen", "O'n to'rt", "Fourteen days — O'n to'rt kun"),
        "15": ("Fifteen", "O'n besh", "Fifteen minutes — O'n besh daqiqa"),
        "16": ("Sixteen", "O'n olti", "Sixteen candles — O'n oltita sham"),
        "17": ("Seventeen", "O'n yetti", "Seventeen flowers — O'n yettita gul"),
        "18": ("Eighteen", "O'n sakkiz", "Eighteen students — O'n sakkizta o'quvchi"),
        "19": ("Nineteen", "O'n to'qqiz", "Nineteen birds — O'n to'qqizta qush"),
        "20": ("Twenty", "Yigirma", "Twenty points — Yigirma ball"),
        "30": ("Thirty", "O'ttiz", "Thirty minutes — O'ttiz daqiqa"),
        "40": ("Forty", "Qirq", "Forty days — Qirq kun"),
        "50": ("Fifty", "Ellik", "Fifty percent — Ellik foiz"),
        "60": ("Sixty", "Oltmish", "Sixty seconds — Oltmish soniya"),
        "70": ("Seventy", "Yetmish", "Seventy kilometers — Yetmish kilometr"),
        "80": ("Eighty", "Sakson", "Eighty meters — Sakson metr"),
        "90": ("Ninety", "To'qson", "Ninety degrees — To'qson daraja"),
        "100": ("One Hundred", "Yuz", "One hundred percent — Yuz foiz mukammal!")
    }
    for num_k, (en_word, uz_word, ex) in numbers_map.items():
        if re.search(rf'\b{num_k}\b', text) and any(w in text for w in ["ingliz", "english", "nima deyiladi", "tarjima", "soni"]):
            return (
                f"🇬🇧 <b>Ingliz tili sabog'i:</b>\n\n"
                f"🔢 <b>{num_k}</b> soni ingliz tilida <b>{en_word}</b> ({uz_word}) deyiladi! 🗣️✨\n\n"
                f"📝 <b>Misol:</b> <i>\"{ex}\"</i>\n\n"
                f"🌟 Talaffuz qilib ko'r: <b>{en_word}</b>! Juda ajoyib! Yana qaysi so'zni o'rganamiz? 🚀"
            )

    # Mashhur inglizcha so'zlar
    vocab_map = {
        "kitob": ("Book", "Kitob", "I like to read a book — Men kitob o'qishni yoqtiraman"),
        "maktab": ("School", "Maktab", "We love our school — Biz maktabimizni sevamiz"),
        "qalam": ("Pencil", "Qalam", "This is my pencil — Bu mening qalamim"),
        "quyosh": ("Sun", "Quyosh", "The sun is shining bright — Quyosh porlab turibdi"),
        "oy": ("Moon", "Oy", "Look at the beautiful moon — Chiroyli oyga qara"),
        "yulduz": ("Star", "Yulduz", "You are a shining star — Sen porloq yulduzsan!"),
        "suv": ("Water", "Suv", "Drink fresh water — Toza suv iching"),
        "olma": ("Apple", "Olma", "An apple a day keeps the doctor away"),
        "mushuk": ("Cat", "Mushuk", "The cat is sleeping — Mushuk uxlayapti"),
        "kuchuk": ("Dog", "Kuchuk", "My dog is friendly — Mening kuchugim do'stona"),
        "do'st": ("Friend", "Do'st", "You are my best friend — Sen mening eng yaxshi do'stimsan")
    }
    for uz_k, (en_w, uz_w, ex_sent) in vocab_map.items():
        if uz_k in text and any(w in text for w in ["ingliz", "english", "tarjima", "nima deyiladi"]):
            return (
                f"🇬🇧 <b>Inglizcha lug'at:</b>\n\n"
                f"📖 <b>{uz_w}</b> so'zi ingliz tilida <b>{en_w}</b> deyiladi! 🗣️✨\n\n"
                f"💡 <b>Gapda qo'llanishi:</b> <i>\"{ex_sent}\"</i>\n\n"
                f"Barakalla! Yangi so'zlarni judayam tez yod olyapsan! 🌟"
            )

    # 3. Koinot va 8 ta sayyora haqida
    if any(w in text for w in ["sayyora", "sayyoralar", "quyosh tizimi", "koinot", "kosmos"]):
        return (
            "🪐 <b>Kichik Allomaning 8 ta Sayyorasi:</b>\n\n"
            "Koinotda Quyosh atrofida 8 ta ajoyib sayyora aylanadi:\n\n"
            "1. 🪐 <b>Merkuriy:</b> Quyoshga eng yaqin, chaqqon va issiq sayyora!\n"
            "2. 🟡 <b>Venera:</b> Eng yorqin, oltin rangli go'zal sayyora!\n"
            "3. 🌍 <b>Yer:</b> Bizning sevimli, hayot va suvlarga to'la yagona uyimiz!\n"
            "4. 🔴 <b>Mars:</b> Qizil sayyora, koinot tadqiqotchilari orzusi!\n"
            "5. 🟠 <b>Yupiter:</b> Koinotning eng ulkan gigant sayyorasi!\n"
            "6. 🪐 <b>Saturn:</b> O'zining sehrli halqalari bilan eng chiroyli sayyora!\n"
            "7. 🔵 <b>Uran:</b> Moviy muzli, eng sovuq sayyoralardan biri!\n"
            "8. 🌊 <b>Neptun:</b> Moviy shamollar va chuqur koinot sirlari sayyorasi!\n\n"
            "Sen qaysi sayyoraga birinchi sayohat qilishni xohlaysan, allomam? 🚀✨"
        )

    # 4. Salomlashish va iliq suhbat
    if any(w in text for w in ["salom", "assalomu alaykum", "qalesan", "qalaysan", "salom alloma"]):
        return (
            "Salom, qadrdon kichik allomam! 🌟 Assalomu alaykum!\n\n"
            "Seni ko'rganimdan judayam xursandman! Men sen bilan matematika misollarini yechishga, "
            "inglizcha qiziqarli so'zlarni o'rganishga, koinot sirlarini kashf etishga va samimiy "
            "suhbatlashishga doim tayyorman! Bugun qanday yangi bilimlarni o'rganamiz? 🚀💖"
        )

    if any(w in text for w in ["rahmat", "katta rahmat", "zo'r", "ajoyib", "raxmat"]):
        return (
            "Arzimaydi, aziz do'stim! 💖 Sen bilan birga ilm o'rganish men uchun katta baxt! "
            "Har doim yangi savollaring bo'lsa bemalol yoz yoki ovozli xabar yubor, men jon deb javob beraman! 🌟👏"
        )

    if any(w in text for w in ["kim san", "kimsan", "isming nima", "o'zing haqingda"]):
        return (
            "Men — <b>Kichik Alloma AI</b> man! 🌟\n\n"
            "Men 7-11 yoshdagi bolajonlar va ularning ota-onalari uchun yaratilgan eng mehribon, dono va quvnoq sun'iy intellekt ustozi va qadrdon do'stiman! "
            "Menga xohlagan savolingni ovozli yoki yozma tarzda berishing mumkin — barchasiga xuddi jonli insonday mehr bilan javob beraman! 😊🚀"
        )

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
