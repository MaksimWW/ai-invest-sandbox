# ==== python-telegram-bot v20 =================================================
import os, logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_TOKEN")  # возьмёт из Secrets

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.WARNING,  # Уменьшаем детализацию
)
# Отключаем логи HTTP запросов
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ──────────────── ХЭНДЛЕРЫ ────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — тестовый ответ"""
    await update.message.reply_text("🤖 Бот теперь работает на python-telegram-bot v20!")

# ─────────────── запуск ───────────────
def run_bot() -> None:
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", cmd_start))
    logger.info("Bot started 🚀 (PTB v20)")
    application.run_polling()

# Позволяет запускать:  python daily_plan_bot_ptb.py
if __name__ == "__main__":
    run_bot()
# ==============================================================================