import os
import subprocess

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "webapp", "audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

audios = [
    {
        "file": "welcome.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Assalomu alaykum, aziz do'stim! Men Kichikalloma Aiman. Bugun Quyosh tizimidagi sakkizta sayyora, ingliz tili, matematika va qiziqarli bilimlarni birgalikda o'rganamiz! Nima haqida gaplashamiz? Mikrofonni bosib bemalol gapiring!"
    },
    {
        "file": "english.mp3",
        "voice": "en-US-AndrewNeural",
        "rate": "-3%",
        "pitch": "+10Hz",
        "text": "Wonderful! Hello my clever friend! What is your favorite animal?"
    },
    {
        "file": "animals.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Hayvonlar olami juda qiziqarli! Masalan, Sher ingliz tilida Layon bo'ladi, Mushuk esa Ket! Siz eng ko'p qaysi hayvonni yoqtirasiz?"
    },
    {
        "file": "math.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Keling, birgalikda oson misol yechamiz! Agar sizda beshta shirin olma bo'lsa va do'stingiz yana beshta bersa, hammasi nechta bo'ladi? Beshga beshni qo'shsak o'nta bo'ladi!"
    },
    {
        "file": "space.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Koinot judayam cheksiz va qiziqarli! Bizning Quyosh tizimimizda sakkizta ajoyib sayyora bor. Yulduzlarni tomosha qilishni yoqtirasizmi?"
    },
    {
        "file": "planets.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Kichik Alloma ekotizimida sakkizta ajoyib sayyora bor! Yer — AI ta'lim, Yupiter — intizom, Venera — virtual do'kon, Saturn — matematika, Merkuriy — kasblar, Uran — ingliz tili, Mars — jismoniy faollik, Neptun — emotsional savodxonlik! Siz qaysi sayyora haqida bilishni xohlaysiz?"
    },
    {
        "file": "merkuriy.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Merkuriy — Ijodkorlik va kasblar sayyorasi! Bu yerda bolalar turli qiziqarli kasblarni kashf etishadi va o'zlarining ijodiy qobiliyatlarini rivojlantirishadi!"
    },
    {
        "file": "venera.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Venera — Virtual Store do'koni! Bolalar boshqa sayyoralarda bilim olib to'plagan oltin tangalariga bu yerda chiroyli avatarlar va buyumlar xarid qilishlari mumkin!"
    },
    {
        "file": "earth.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Yer — Kognitiv ta'lim va AI Tutor sayyorasi! Bu yerda Sokratik usulda Kichikalloma AI bilan suhbatlashib, chuqur bilim va fikrlash o'rganiladi!"
    },
    {
        "file": "mars.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Mars — Jismoniy faollik va sport sayyorasi! Bu yerda bolajonlar jismoniy mashqlar, badantarbiya va harakatli sog'lom mashg'ulotlarni bajarishadi!"
    },
    {
        "file": "jupiter.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Yupiter — O'z-o'zini boshqarish va intizom sayyorasi! Bu yerda kunlik rejalashtirish, vazifalarni bajarish va intizom shakllantiriladi!"
    },
    {
        "file": "saturn.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Saturn — Matematika va mantiq sayyorasi! Bu yerda yoshga mos qiziqarli matematik misollar, mantiqiy savollar va testlar yechiladi!"
    },
    {
        "file": "uran.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Uran — English Vocabulary, ya'ni inglizcha so'z boyligi sayyorasi! Bu yerda inglizcha yangi so'zlar, to'g'ri talaffuz va testlar o'rganiladi!"
    },
    {
        "file": "neptune.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Neptun — Emotsional savodxonlik sayyorasi! Bu yerda bolalar o'z his-tuyg'ularini tanish, mehr-oqibat va yaxshi kayfiyatni shakllantirishadi!"
    },
    {
        "file": "startup.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Kichik Alloma — bu 7 yoshdan 11 yoshgacha bo'lgan bolalar va ota-onalar uchun mo'ljallangan, sakkizta sayyoradan iborat rivojlanish ekotizimidir! Asoschisi — Komiljonov Shoxruxbek!"
    },
    {
        "file": "founder.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Kichik Alloma loyihasining asoschisi va bosh dasturchisi — Komiljonov Shoxruxbek Komiljon o'g'li! Rasmiy sayti — kichikalloma.uz!"
    },
    {
        "file": "tarbiya.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Kattalarga salom berish va har doim ochiq yuz bilan muomala qilish — eng go'zal odobdir! Siz judayam odobli va aqlli bola ekansiz, barakalla!"
    },
    {
        "file": "cartoons.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Qoyil! Bu juda qiziqarli mavzu! Sevimli qahramoningiz yoki o'yiningiz haqida yana aytib bering, maroq bilan eshitaman!"
    },
    {
        "file": "riddle.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Sizga bitta topishmoq aytaman, toping-chi: Kunduzi uxlaydi, kechasi nur sochadi? Bu nima bo'lishi mumkin? Albatta, bu — Oy!"
    },
    {
        "file": "general.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Men sizni diqqat bilan eshityapman, aziz do'stim! Keling, birgalikda sayyoralar, ingliz tili, matematika yoki boshqa qiziqarli bilimlarni o'rganamiz! Nima haqida gaplashamiz?"
    },
    {
        "file": "qalesan.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Assalomu alaykum! Rahmat, men juda zo'rman! O'zing yaxshimisan, ahvollaring qalay? Isming nima, aziz do'stim?"
    },
    {
        "file": "mood_good.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Kayfiyating a'lo ekanidan juda xursandman! Isming nima, aziz do'stim?"
    },
    {
        "file": "name_ask.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Tanishganimdan juda xursandman! Isming judayam chiroyli ekan! Nechanchi sinfda o'qiysan?"
    },
    {
        "file": "grade_response.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Barakalla! Juda a'lochi o'quvchi ekansan! Keling, birgalikda 8 ta sayyora, ingliz tili yoki qiziqarli matematika o'rganamiz! Qaysi biridan boshlaymiz?"
    },
    {
        "file": "thanks.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Arzimiydi, do'stim! Sizga yordam berishdan har doim xursandman!"
    },
    {
        "file": "goodbye.mp3",
        "voice": "uz-UZ-SardorNeural",
        "rate": "+1%",
        "pitch": "+14Hz",
        "text": "Xayr, aziz do'stim! Ko'rishguncha! O'qishlaringda katta omadlar tilayman!"
    },
    {
        "file": "friend.mp3",
        "voice": "en-US-AndrewNeural",
        "rate": "-10%",
        "pitch": "+10Hz",
        "text": "Friend! Frend! Do'st."
    },
    {
        "file": "knowledge.mp3",
        "voice": "en-US-AndrewNeural",
        "rate": "-10%",
        "pitch": "+10Hz",
        "text": "Knowledge! Nolidj! Bilim."
    },
    {
        "file": "sun.mp3",
        "voice": "en-US-AndrewNeural",
        "rate": "-10%",
        "pitch": "+10Hz",
        "text": "Sun! San! Quyosh."
    },
    {
        "file": "star.mp3",
        "voice": "en-US-AndrewNeural",
        "rate": "-10%",
        "pitch": "+10Hz",
        "text": "Star! Star! Yulduz."
    }
]

for item in audios:
    out_path = os.path.join(AUDIO_DIR, item["file"])
    regenerate_list = [
        "planets.mp3", "merkuriy.mp3", "venera.mp3", "earth.mp3", "mars.mp3",
        "jupiter.mp3", "saturn.mp3", "uran.mp3", "neptune.mp3", "startup.mp3",
        "founder.mp3"
    ]
    if os.path.exists(out_path) and item["file"] not in regenerate_list:
        print(f"Skipping existing {item['file']}")
        continue
    print(f"Generating {item['file']} with voice {item['voice']}...")
    cmd = [
        "edge-tts",
        "--voice", item["voice"],
        "--rate", item["rate"],
        "--pitch", item["pitch"],
        "--text", item["text"],
        "--write-media", out_path
    ]
    subprocess.run(cmd, check=True)

print("Barcha audio fayllar muvaffaqiyatli yaratildi!")
