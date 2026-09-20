import os
import sys
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
    print("\n" + "=" * 50)
    print("XATOLIK: BOT_TOKEN topilmadi yoki kiritilmadi!")
    print("Iltimos, .env faylini oching va Telegram @BotFather dan")
    print("olgan bot tokeningizni kiriting:")
    print("BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ")
    print("=" * 50 + "\n")
