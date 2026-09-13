import asyncio
import logging
import os
import sys
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    BotCommand,
    BotCommandScopeDefault,
    MenuButtonWebApp,
    WebAppInfo
)

from config import BOT_TOKEN
from handlers import router
from keyboards import DEFAULT_WEBAPP_URL

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def health_check(request):
    return web.Response(text="Kichik Alloma AI Bot 24/7 is Running! 🚀")

async def start_web_server():
    """Render.com Web Service uchun bepul port eshitish serveri"""
    try:
        app = web.Application()
        app.router.add_get("/", health_check)
        app.router.add_get("/health", health_check)
        runner = web.AppRunner(app)
        await runner.setup()
        port = int(os.environ.get("PORT", 8080))
        site = web.TCPSite(runner, "0.0.0.0", port)
        await site.start()
        logger.info(f"Render Web Service uchun {port}-portda web server ishga tushdi.")
    except Exception as e:
        logger.warning(f"Web serverni ishga tushirishda ogohlantirish: {e}")

async def setup_bot_commands(bot: Bot) -> None:
    """Telegramning pastki chap burchagidagi doimiy Menu tugmasiga Mini App ni o'rnatish"""
    try:
        # 1. Pastdagi asosiy Menu tugmasini to'g'ridan-to'g'ri Mini App ga aylantirish
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="🚀 Kichik Alloma AI",
                web_app=WebAppInfo(url=DEFAULT_WEBAPP_URL)
            )
        )
        # 2. Komandalar ro'yxati
        commands = [
            BotCommand(command="start", description="🔄 Boshlash / Yangilash"),
            BotCommand(command="help", description="🆘 Yordam va adminga yozish"),
            BotCommand(command="settings", description="⚙️ Sozlamalar va til tanlash"),
        ]
        await bot.set_my_commands(commands=commands, scope=BotCommandScopeDefault())
        logger.info("Bot komandalar menyusi va Mini App Menu tugmasi muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.warning(f"Buyruqlar menyusini o'rnatishda xatolik: {e}")

async def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("BOT_TOKEN ko'rsatilmagan! Iltimos, .env faylga token kiriting.")
        sys.exit(1)

    # Render.com da 24/7 port ochish
    await start_web_server()

    while True:
        try:
            bot = Bot(
                token=BOT_TOKEN,
                default=DefaultBotProperties(parse_mode=ParseMode.HTML)
            )
            dp = Dispatcher()
            dp.include_router(router)

            await bot.delete_webhook(drop_pending_updates=True)
            await setup_bot_commands(bot)
            
            logger.info("Bot muvaffaqiyatli ulandi va xabarlarni kutmoqda...")
            await dp.start_polling(bot, handle_signals=False)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot to'xtatildi.")
            break
        except Exception as e:
            logger.error(f"Ulanishda xatolik yoki internet uzilishi: {e}. 3 soniyada qayta ulanadi...")
            await asyncio.sleep(3)
        finally:
            try:
                await bot.session.close()
            except Exception:
                pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot yakunlandi.")
