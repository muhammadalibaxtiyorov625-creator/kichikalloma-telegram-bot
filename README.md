# 🚀 Telegram Bot va Telegram Mini App (Web App)

Ushbu loyiha Python (`aiogram 3`) asosidagi Telegram bot va unga to'liq integratsiya qilingan **Telegram Mini App** (Web App) dan iborat.

---

## 📁 Loyiha tuzilmasi

```text
tekegram/
├── .env                # Bot tokeni saqlanadigan konfiguratsiya
├── .env.example        # Namuna konfiguratsiya
├── config.py           # Sozlamalarni yuklovchi modul
├── main.py             # Botni ishga tushirish fayli
├── handlers.py         # Bot komandalari va xabarlarni qayta ishlovchi
├── keyboards.py        # Tugmalar (Menu va Inline WebApp tugmalari)
├── requirements.txt    # Kerakli Python kutubxonalari
├── server.py           # Mini Appni lokal sinash uchun server
└── webapp/
    └── index.html      # Telegram Mini App interfeysi (HTML + JS + CSS)
```

---

## ⚙️ 1-Qadam: Bot Tokenini olish va sozlash

1. Telegramda **[@BotFather](https://t.me/BotFather)** ga kiring.
2. `/newbot` buyrug'ini yuboring va botingizga nom hamda username bering.
3. BotFather sizga **HTTP API Token** beradi (masalan: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
4. Ushbu papkadagi `.env` faylini oching va tokenni yozing:
   ```env
   BOT_TOKEN=SIZNING_TOKENINGIZ
   ```

---

## ▶️ 2-Qadam: Botni ishga tushirish

Terminalda (PowerShell yoki CMD) quyidagi buyruqni bajaring:

```bash
python main.py
```

Endi Telegramda o'z botingizga kirib **/start** buyrug'ini yuboring! 🎉

---

## 📱 3-Qadam: Telegram Mini App (Web App) ni ulash

1. Mini App fayli: `webapp/index.html`.
2. Telegram faqat **HTTPS** havolalarni qabul qiladi. Shuning uchun `webapp` papkasini:
   - **GitHub Pages** (bepul)
   - **Vercel** (bepul)
   - yoki **ngrok** / **Cloudflare Tunnel** orqali internetga chiqarasiz.
3. Hosil bo'lgan HTTPS havolani `keyboards.py` faylidagi `WEB_APP_URL` o'zgaruvchisiga yozasiz:
   ```python
   WEB_APP_URL = "https://sizning-saytingiz.vercel.app"
   ```
4. Shuningdek, **[@BotFather](https://t.me/BotFather)** orqali botingizning pastki chap burchagiga doimiy **Menu Button** (Mini App tugmasi) qilib ham o'rnatishingiz mumkin:
   - `/mybots` -> Botingizni tanlang -> **Bot Settings** -> **Menu Button** -> **Configure menu button** -> Web App havolasini yuboring.

---

## 💻 Mini Appni brauzerda sinab ko'rish

Mini Appni kompyuteringiz brauzerida ochib ko'rish uchun:
```bash
python server.py
```
va brauzerda `http://localhost:8080` manziliga kiring.
