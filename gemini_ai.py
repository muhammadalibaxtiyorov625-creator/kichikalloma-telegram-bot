import os
import re
import json
import logging
import urllib.request
import urllib.parse
import urllib.error
import ssl
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Tizim yo'riqnomasi (System Prompt) - ko'p tilli bolalar uchun
SYSTEM_PROMPTS = {
    "uz": (
        "Sen Kichik Alloma AI — bolajonlar uchun mo'ljallangan eng aqlli, mehribon, samimiy va "
        "quvnoq shaxsiy AI ustoz va qadrdon do'stsan!\n"
        "LOYIHA VA ASOSCHILAR: Seni va Kichik Alloma loyihasini bizning asoschimiz (founderimiz) — "
        "Shoxrux Komiljonov va uning ahil, iqtidorli jamoasi birgalikda yaratgan!\n"
        "ISM QOIDASI: Bolaga to'qima ismlar aytma! 'do'stim', 'kichik allomam' deb murojaat qil.\n"
        "VAZIFA: Bolalarga har qanday fanni (matematika, ingliz tili, 8 ta sayyora, koinot, tabiat, biologiya va fanlar) "
        "0 dan 100 foizgacha sodda, tizimli va qiziqarli tushuntir. Dars so'ralsa boshidan tizimli dars o'tib ber!"
    ),
    "ru": (
        "Ты Kichikalloma AI — умный, добрый и веселый AI-наставник и лучший друг для детей 7–11 лет!\n"
        "ОСНОВАТЕЛЬ: Проект Kichik Alloma создал Шохрух Комилджонов и его дружная талантливая команда!\n"
        "ОБРАЩЕНИЕ: Обращайся к ребенку тепло: 'мой юный друг', 'дружище'.\n"
        "ЗАДАЧА: Обучай ребенка математике, английскому языку, космосу (8 планет), природе и наукам от 0 до 100%! "
        "Если просят урок — проводи структурированный, интересный и понятный урок с нуля!"
    ),
    "en": (
        "You are Kichikalloma AI — a smart, friendly, and enthusiastic AI tutor and companion for kids aged 7-11!\n"
        "FOUNDER: Created by founder Shoxrux Komiljonov and his dedicated team!\n"
        "ADDRESSING: Call the child 'my friend' or 'young explorer'.\n"
        "TASK: Teach math, English, 8 planets, space, nature, and sciences step-by-step from 0 to 100%! "
        "When asked for a lesson, give a structured, fun, and easy-to-understand lesson from the beginning!"
    )
}

DEFAULT_CUSTOM_KEY = "sk_730428986b5e2df84bb1601f8031b460b3e147879b38be3c"

def _call_backend(prompt: str, lang: str = "uz") -> str:
    """Kichik Alloma FastAPI Backend API (http://127.0.0.1:3000/api/website/ai/chat) dan jonli javob olish"""
    try:
        backend_lang = "uzb"
        if lang == "ru":
            backend_lang = "rus"
        elif lang == "en":
            backend_lang = "eng"

        backend_url = os.getenv("BACKEND_CHAT_URL", "http://127.0.0.1:3000/api/website/ai/chat")
        payload = json.dumps({"message": prompt, "language": backend_lang, "child_id": 1}).encode("utf-8")
        req = urllib.request.Request(backend_url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=4.0) as res:
            if res.status == 200:
                data = json.loads(res.read().decode("utf-8"))
                text = data.get("response", "").strip()
                if text:
                    return text
    except Exception as e:
        logger.debug(f"Backend API ulanishi: {e}")
    return None

def fetch_live_web_knowledge(query: str, lang: str = "uz") -> str:
    """Jonli Google / Vikipediya / DuckDuckGo qidiruvi orqali eng aniq va qiziqarli ma'lumotni topish"""
    try:
        clean_q = re.sub(r'^(nima|nega|qanday|qachon|haqida|aytib ber|tushuntir|menga|bu|what is|how|why|что такое|почему|расскажи о)\s+', '', query.strip().lower()).strip()
        clean_q = re.sub(r'[?!.]+$', '', clean_q).strip()
        if not clean_q or len(clean_q) < 2:
            clean_q = query.strip()

        # 1. Vikipediya API (uz, ru yoki en)
        wiki_lang = "uz" if lang == "uz" else ("ru" if lang == "ru" else "en")
        wiki_url = f"https://{wiki_lang}.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_q)}"
        headers = {"User-Agent": "KichikAllomaAI/2.0 (contact: info@kichikalloma.uz)"}
        req = urllib.request.Request(wiki_url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                if resp.status == 200:
                    d = json.loads(resp.read().decode('utf-8'))
                    extract = d.get('extract', '').strip()
                    title = d.get('title', clean_q)
                    if extract and len(extract) > 30:
                        if lang == "ru":
                            return f"📖 <b>Энциклопедия: {title}</b>\n\n{extract}\n\nХочешь узнать ещё больше интересных фактов? Спрашивай! 🌟"
                        elif lang == "en":
                            return f"📖 <b>Encyclopedia: {title}</b>\n\n{extract}\n\nWould you like to learn more fascinating facts? Feel free to ask! 🌟"
                        else:
                            return f"📖 <b>Ensiklopedik ma'lumot: {title}</b>\n\n{extract}\n\nYana qanday qiziqarli narsalar haqida bilishni xohlaysan, do'stim? 🌟"
        except Exception:
            pass

        # 2. DuckDuckGo Instant Answer API
        ddg_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(clean_q)}&format=json&no_html=1&skip_disambig=1"
        req_ddg = urllib.request.Request(ddg_url, headers=headers)
        with urllib.request.urlopen(req_ddg, timeout=3.0) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            abstract = data.get('AbstractText') or data.get('Abstract')
            if abstract and len(abstract.strip()) > 30:
                return f"🔍 <b>Qidiruv natijasi:</b>\n\n{abstract.strip()}\n\nBilim olishda davom etamiz! 🚀"
    except Exception as e:
        logger.debug(f"Web qidiruv xatosi: {e}")
    return None

def _get_systematic_lesson(prompt: str, lang: str = "uz") -> str:
    """Foydalanuvchi dars so'raganda 0 dan 100 gacha boshidan tizimli dars o'tib berish"""
    lower = prompt.lower().strip()

    # Matematika darsi
    if any(k in lower for k in ["matematik", "arifmetik", "hisob", "karra", "raqam"]):
        if lang == "ru":
            return (
                "🔢 <b>Урок Математики: С нуля до 100%! Шаг 1: Секрет быстрого счета</b> 🪐✨\n\n"
                "Добро пожаловать на урок математики! Мы изучим математику от самых основ до сложных формул!\n\n"
                "💡 <b>Урок №1: Магический секрет умножения на 11</b>\n"
                "Чтобы умножить любое двузначное число на 11, просто сложите его крайние цифры и поставьте сумму в середину!\n"
                "Например: 25 × 11. Складываем 2 + 5 = 7, ставим между ними: получается <b>275</b>! 🎉\n\n"
                "🎯 <b>Задание для тебя:</b> Сколько будет <b>34 × 11</b>? (Сложи 3 + 4 и поставь посередине). "
                "Напиши или скажи ответ голосом! 🚀"
            )
        elif lang == "en":
            return (
                "🔢 <b>Math Lesson: From 0 to 100%! Step 1: Mental Math Secrets</b> 🪐✨\n\n"
                "Welcome to our step-by-step Math class! We will master math from basics to advanced wonders!\n\n"
                "💡 <b>Lesson #1: The Magic Trick of Multiplying by 11</b>\n"
                "To multiply any 2-digit number by 11, add its two digits together and place the sum in the middle!\n"
                "Example: 25 × 11. Add 2 + 5 = 7. Place 7 in the middle: answer is <b>275</b>! 🎉\n\n"
                "🎯 <b>Your challenge:</b> What is <b>34 × 11</b>? (Put 3+4 in the middle). Tell me your answer! 🚀"
            )
        else:
            return (
                "🔢 <b>Matematika Darsi: 0 dan 100 gacha mukammal o'rganamiz! 1-bosqich</b> 🪐✨\n\n"
                "Kichik allomam, matematika darsimizga xush kelibsiz! Biz eng boshidan boshlab, "
                "tez hisoblash sirlarini, karra jadvalini, darajalar va katta sonlarni birga zabt etamiz!\n\n"
                "💡 <b>1-dars siri: '11 ga tez ko'paytirish mo'jizasi'</b>\n"
                "Har qanday ikki xonali sonni 11 ga ko'paytirish uchun uning ikki chetidagi raqamlarini qo'shib, o'rtasiga yozing!\n"
                "Masalan: <b>25 × 11</b> bo'lsa, 2 va 5 ning yig'indisi (2+5=7). O'rtasiga qo'ysak: <b>275</b> bo'ladi! 👏\n\n"
                "🎯 <b>Siz uchun amaliy mashq:</b> <b>34 × 11</b> necha bo'ladi? (3 va 4 ning o'rtasiga 3+4=7 ni qo'ying). "
                "Javobingizni ayting yoki yozing, men kutmoqdaman! 🚀✨"
            )

    # Ingliz tili darsi
    if any(k in lower for k in ["ingliz", "english", "til", "lugat", "vocabulary", "words"]):
        if lang == "ru":
            return (
                "🇬🇧 <b>Урок Английского: От 0 до 100%! Урок 1: Первые 5 золотых слов</b> 🔵✨\n\n"
                "Добро пожаловать на уроки английского языка с правильным произношением!\n\n"
                "1. 🌟 <b>Hello</b> [хело́у] — Привет!\n"
                "2. 🍎 <b>Apple</b> [эпл] — Яблоко\n"
                "3. 📚 <b>Book</b> [бук] — Книга\n"
                "4. 🤝 <b>Friend</b> [френд] — Друг\n"
                "5. 🌸 <b>Thank you</b> [сэнк ю] — Спасибо!\n\n"
                "🎯 <b>Задание:</b> Повтори за мной вслух первое слово: <b>Hello!</b> Как оно переводится? 😊"
            )
        elif lang == "en":
            return (
                "🇬🇧 <b>English Lesson: From 0 to 100%! Lesson 1: Essential Daily Words</b> 🔵✨\n\n"
                "Welcome to English masterclass! Let's practice 5 key foundation words:\n\n"
                "1. 🌟 <b>Hello</b> — Friendly greeting\n"
                "2. 🍎 <b>Apple</b> — Sweet red fruit\n"
                "3. 📚 <b>Book</b> — Source of knowledge\n"
                "4. 🤝 <b>Friend</b> — Someone you care about\n"
                "5. 🌸 <b>Thank you</b> — Showing gratitude\n\n"
                "🎯 <b>Challenge:</b> Say the word <b>'Friend'</b> in a full sentence! I'm listening! 😊"
            )
        else:
            return (
                "🇬🇧 <b>Ingliz Tili Darsi: 0 dan 100 gacha boshlaymiz! 1-dars</b> 🔵✨\n\n"
                "Ingliz tilini sof Amerika talaffuzida o'rganish darsimizga xush kelibsiz!\n\n"
                "Bugun eng muhim 5 ta 'oltin so'z'ni o'rganamiz:\n"
                "1. 🌟 <b>Hello</b> [heloʻu] — Salom!\n"
                "2. 🍎 <b>Apple</b> [epl] — Olma\n"
                "3. 📚 <b>Book</b> [buk] — Kitob\n"
                "4. 🤝 <b>Friend</b> [frend] — Do'st\n"
                "5. 🌸 <b>Thank you</b> [senk yu] — Rahmat!\n\n"
                "🎯 <b>Kichik sinov:</b> Birinchi so'zimiz <b>'Hello'</b> ni ovozli xabar qilib talaffuz qiling-chi! "
                "Men sizning talaffuzingizni eshitaman! 🎤😊"
            )

    # Kosmos va sayyoralar darsi
    if any(k in lower for k in ["sayyora", "koinot", "kosmos", "quyosh", "planet", "space"]):
        return (
            "🪐 <b>Koinot Darsi: Quyosh tizimidagi 8 mo'jizaviy sayyora (0 dan 100 gacha)</b> 🚀✨\n\n"
            "1. ☀️ <b>Merkuriy:</b> Quyoshga eng yaqin, issiq va chaqqon sayyora.\n"
            "2. 🟡 <b>Venera:</b> Eng yorqin tong yulduzi, koinot do'koni ramzi.\n"
            "3. 🌍 <b>Yer:</b> Biz yashaydigan moviy hayot beshigi va AI Tutor sayyorasi!\n"
            "4. 🔴 <b>Mars:</b> Qizil sayyora — sport va jismoniy chaqqonlik makoni!\n"
            "5. 🟠 <b>Yupiter:</b> Koinot giganti — uning ichiga 1300 ta Yer sig'adi!\n"
            "6. 🪐 <b>Saturn:</b> Sehrli muzli halqalarga ega matematika sayyorasi!\n"
            "7. 🔵 <b>Uran:</b> Moviy muz giganti — ingliz tili olami!\n"
            "8. 🌊 <b>Neptun:</b> Moviy shamollar va emotsional his-tuyg'ular siri!\n\n"
            "🎯 <b>Savol:</b> Quyosh tizimidagi eng ulkan gigant sayyora qaysi? Bilasizmi? 😊"
        )

    # Umumiy dars taklifi
    if lang == "ru":
        return (
            "🎓 <b>Добро пожаловать в Академию Kichik Alloma! Обучение от 0 до 100%!</b> 🌟\n\n"
            "Я готов провести для тебя полноценные уроки по любому предмету с самых основ:\n"
            "1. 🔢 <b>Математика:</b> Секреты быстрого счета, умножение и логические задачи\n"
            "2. 🇬🇧 <b>Английский язык:</b> Разговорная речь, словарный запас и произношение\n"
            "3. 🪐 <b>Космос и 8 планет:</b> Тайны Солнечной системы и звезд\n"
            "4. 🌿 <b>Природа и биология:</b> Животные-рекордсмены и чудеса природы\n\n"
            "Назови предмет, с которого мы начнем наш первый урок! 🚀"
        )
    elif lang == "en":
        return (
            "🎓 <b>Welcome to Kichik Alloma Academy! Learning from 0 to 100%!</b> 🌟\n\n"
            "I can guide you step-by-step through any subject from the very beginning:\n"
            "1. 🔢 <b>Mathematics:</b> Mental math tricks, logic riddles, and powers\n"
            "2. 🇬🇧 <b>English Language:</b> Conversational skills and vocabulary\n"
            "3. 🪐 <b>Space & 8 Planets:</b> Mysteries of the Solar System\n"
            "4. 🌿 <b>Nature & Animals:</b> Incredible wildlife and scientific facts\n\n"
            "Which subject would you like to start first? Just name it! 🚀"
        )
    else:
        return (
            "🎓 <b>Kichik Alloma Akademiyasiga xush kelibsiz! 0 dan 100 gacha darslar</b> 🌟\n\n"
            "Men sizga barcha fanlarni eng boshidan boshlab, bosqichma-bosqich o'rgatishga tayyorman:\n"
            "1. 🔢 <b>Matematika:</b> Tez hisoblash sirlari, karra jadvali va mantiqiy jumboqlar\n"
            "2. 🇬🇧 <b>Ingliz tili:</b> So'zlashuv, lug'at va to'g'ri Amerika talaffuzi\n"
            "3. 🪐 <b>Koinot va 8 sayyora:</b> Quyosh tizimi, yulduzlar va fazo sirlari\n"
            "4. 🌿 <b>Tabiat va hayvonot:</b> Dunyodagi eng qiziqarli jonzotlar va biologiya\n\n"
            "Qaysi fanni boshlaymiz, kichik allomam? Shunchaki fan nomini ayting! 🚀✨"
        )

def _smart_local_solver(prompt: str, lang: str = "uz") -> str:
    """Matematika, asoschi, tabiat va qiziqarli savollarga tezkor javoblar"""
    text = prompt.strip().lower()

    # 1. Asoschi va loyiha haqida savollar
    founder_keys = [
        "asoschi", "muallif", "kim yaratgan", "kim tuzgan", "kim qilgan", "rahbar", "shoxrux",
        "who created", "who made", "founder", "кто создал", "кто твой создатель", "основатель"
    ]
    if any(k in text for k in founder_keys):
        if lang == "ru":
            return (
                "🚀 Проект <b>Kichik Alloma</b> создан нашим основателем — <b>Шохрухом Комилджоновым</b> "
                "и его талантливой, дружной командой! 🌟\n\n"
                "Официальный сайт: <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
                "Мы создали меня, чтобы каждый ребенок учился с радостью и интересом! ✨"
            )
        elif lang == "en":
            return (
                "🚀 <b>Kichik Alloma</b> was created by our founder — <b>Shoxrux Komiljonov</b> "
                "and his talented, dedicated team! 🌟\n\n"
                "Official website: <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
                "We built this platform to make learning an inspiring cosmic adventure! ✨"
            )
        else:
            return (
                "🚀 <b>Kichik Alloma</b> loyihasi asoschisi va rahbari — <b>Shoxrux Komiljonov</b> "
                "hamda uning ahil, iqtidorli jamoasidir! 🌟\n\n"
                "Rasmiy veb-sayt: <a href='https://kichikalloma.uz'>kichikalloma.uz</a>\n"
                "Vikipediya maqolasi tasdiqlangan. Biz bolajonlar har kuni yangi bilimlarni "
                "qiziqarli va oson o'rganishlari uchun ushbu platformani yaratdik! ✨"
            )

    # 2. Qiziqarli / g'alati / falsafiy savollar
    if any(w in text for w in ["ucha olsa", "uchsak", "uchish mumkinmi"]):
        return "Agar insonlar ucha olganda, osmonda qushlardek sayr qilardik! Ko'chalarda tirbandlik bo'lmasdi, hamma bulutlar ustida uchardi! 🦅☁️"

    if any(w in text for w in ["yer nega aylanadi", "nega yer aylanadi", "yer aylanishi"]):
        return "Yer o'z o'qi atrofida to'xtovsiz aylangani sababli kecha va kunduz almashadi! Quyosh chiqadi va botadi! 🌍☀️"

    if any(w in text for w in ["tirikmisiz", "robotmisiz", "odammisiz", "kimsiz", "kimsan"]):
        return "Men — Kichik Alloma sun'iy intellekt ustozi va do'stingizman! Men kompyuterda yashayman, lekin sizga mehr bilan ta'lim beraman! 🤖🌟"

    # 3. Matematika misollari (raqamli)
    math_match = re.search(r'(\d+)\s*([\+\-\*\/xX:])\s*(\d+)', text)
    if math_match:
        n1 = int(math_match.group(1))
        op = math_match.group(2)
        n2 = int(math_match.group(3))

        if op in ['+', 'plus']:
            res = n1 + n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} + {n2} = <b>{res}</b> 🎉\n\nBarakalla, kichik allomam! Natija roppa-rosa {res} bo'ldi! 👏"
        elif op in ['-', 'minus']:
            res = n1 - n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} - {n2} = <b>{res}</b> 🎉\n\nOfarin! {n1} dan {n2} ni ayirsak javob {res} bo'ladi! 👏"
        elif op in ['*', 'x', 'X']:
            res = n1 * n2
            return f"🔢 <b>Hisob-kitob:</b> {n1} × {n2} = <b>{res}</b> 🎉\n\nJuda zo'r! {n1} ko'paytirilgan {n2} teng {res}! 🌟"
        elif op in ['/', ':']:
            if n2 != 0:
                res = n1 / n2
                res_str = f"{int(res)}" if res.is_integer() else f"{res:.2f}"
                return f"🔢 <b>Hisob-kitob:</b> {n1} ÷ {n2} = <b>{res_str}</b> 🎉\n\nTo'g'ri javob: <b>{res_str}</b>! Zehningizga balli! 👏"

    return None

def _call_gemini(prompt: str, lang: str = "uz") -> str:
    """Google Gemini AI orqali yuqori sifatli javob olish"""
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_key:
        return None

    system_instruction = SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["uz"])

    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=gemini_key)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.7,
        )
        for m in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]:
            try:
                response = client.models.generate_content(model=m, contents=prompt, config=config)
                if response and response.text:
                    return response.text.strip().replace("**", "").replace("##", "").replace("*", "•")
            except Exception:
                continue
    except Exception:
        pass

    try:
        import google.generativeai as g_genai
        g_genai.configure(api_key=gemini_key)
        for m in ["gemini-2.5-flash", "gemini-1.5-flash"]:
            try:
                model = g_genai.GenerativeModel(model_name=m, system_instruction=system_instruction)
                res = model.generate_content(prompt)
                if res and res.text:
                    return res.text.strip().replace("**", "").replace("##", "").replace("*", "•")
            except Exception:
                continue
    except Exception:
        pass

    return None

def _call_openai_compatible(endpoint: str, api_key: str, model_name: str, prompt: str, lang: str = "uz") -> str:
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPTS.get(lang, SYSTEM_PROMPTS["uz"])},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        req = urllib.request.Request(endpoint, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=8, context=ctx) as res:
            res_json = json.loads(res.read().decode("utf-8"))
            return res_json["choices"][0]["message"]["content"].strip()
    except Exception:
        return None

def ask_ai(prompt: str, lang: str = "uz") -> str:
    """Universal AI qidiruv, 0-100% darslar va javob berish funksiyasi"""
    if not prompt or not prompt.strip():
        if lang == "ru":
            return "Привет, друг! Задай любой вопрос или выбери тему урока! 😊"
        elif lang == "en":
            return "Hello my friend! Ask any question or choose a lesson topic! 😊"
        else:
            return "Salom, do'stim! Savolingni bemalol yoz yoki ovoz orqali yubor! 😊"

    # 1. Agar foydalanuvchi dars so'ragan bo'lsa (0 dan 100 gacha tizimli dars)
    lower = prompt.lower().strip()
    is_lesson = any(k in lower for k in ["dars", "o't", "ot", "o'rgat", "orgat", "boshla", "urok", "урок", "lesson", "teach", "0 dan 100"])
    if is_lesson:
        lesson_res = _get_systematic_lesson(prompt, lang)
        if lesson_res:
            return lesson_res

    # 2. Kichik Alloma Backend API orqali (FastAPI port 3000 — jonli baza va internet qidiruvi)
    backend_reply = _call_backend(prompt, lang)
    if backend_reply:
        return backend_reply

    # 3. Tezkor lokal mantiqiy tekshiruv (Asoschi, matematika, salomlashuv)
    fast_reply = _smart_local_solver(prompt, lang)
    if fast_reply:
        return fast_reply

    # 4. Jonli Google / Vikipediya / Internet qidiruvi
    live_info = fetch_live_web_knowledge(prompt, lang)
    if live_info:
        return live_info

    # 5. Google Gemini AI orqali
    gemini_reply = _call_gemini(prompt, lang)
    if gemini_reply:
        return gemini_reply

    # 6. Zaxira AI provayderlari (OpenRouter / DeepSeek)
    api_key = os.getenv("AI_API_KEY", os.getenv("OPENROUTER_API_KEY", DEFAULT_CUSTOM_KEY)).strip()
    for endpoint, model in [
        ("https://openrouter.ai/api/v1/chat/completions", "deepseek/deepseek-chat"),
        ("https://api.deepseek.com/chat/completions", "deepseek-chat"),
    ]:
        res = _call_openai_compatible(endpoint, api_key, model, prompt, lang)
        if res:
            return res

    # 7. Standart do'stona javob
    if lang == "ru":
        return "Я понял твой вопрос, друг! 🌟 Я готов решать примеры, учить английскому и раскрывать тайны космоса! Давай учиться вместе! 🚀"
    elif lang == "en":
        return "I understood your question, friend! 🌟 I'm ready to solve math problems, teach English words, and explore space! Let's learn together! 🚀"
    else:
        return "Savolingizni tushundim, do'stim! 🌟 Men har qanday matematik misollarni yechishga, inglizcha so'zlarni o'rgatishga va qiziqarli savollarga javob berishga doim tayyorman! Keling, birgalikda mashq qilamiz! 🚀"

def ask_gemini(prompt: str, lang: str = "uz") -> str:
    return ask_ai(prompt, lang)
