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
    level=logging.INFO,  # Включаем подробные логи для отладки
)
# Включаем логи для отладки
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("telegram").setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# ──────────────── ХЭНДЛЕРЫ ────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — приветствие и краткая справка"""
    try:
        logger.info(f"Команда /start от пользователя {update.effective_user.id}")
        
        message = """🤖 **AI Invest PlanBot запущен!**

📊 Доступные команды:
• /help - полная справка по командам
• /prices - текущие цены акций
• /signals - торговые сигналы  
• /status - статус системы

💡 Отправьте /help для подробной информации!"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("Команда /start выполнена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await update.message.reply_text("❌ Произошла ошибка при выполнении команды /start")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — справка по командам"""
    try:
        logger.info(f"Команда /help от пользователя {update.effective_user.id}")
        
        message = """🤖 **Справка по командам AI Invest PlanBot**

📈 **Торговые команды:**
• `/prices` - показать текущие цены акций YNDX, FXIT
• `/signals` - получить торговые сигналы для акций

⚙️ **Системные команды:**
• `/status` - проверить статус подключений (Tinkoff API, Google Sheets)
• `/help` - показать эту справку
• `/start` - перезапустить бота

📊 **О боте:**
Бот анализирует рынок акций, генерирует торговые сигналы и ведет автоматическую отчетность."""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("Команда /help выполнена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_help: {e}")
        await update.message.reply_text("❌ Произошла ошибка при выполнении команды /help")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/prices — показать текущие цены акций"""
    try:
        logger.info(f"Команда /prices от пользователя {update.effective_user.id}")
        
        message = """📈 **Текущие цены акций**

⚠️ DEMO режим - тестовые данные:

• **YNDX**: 2,450.50 ₽ 📈 (+1.2%)
• **FXIT**: 1,180.25 ₽ 📉 (-0.8%)

🕐 Обновлено: только что
💡 Для реальных данных требуется настройка Tinkoff API"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("Команда /prices выполнена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_prices: {e}")
        await update.message.reply_text(f"❌ Ошибка получения цен: {str(e)}")

async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/signals — показать торговые сигналы"""
    try:
        logger.info(f"Команда /signals от пользователя {update.effective_user.id}")
        
        message = """📊 **Торговые сигналы**

⚠️ DEMO режим - тестовые сигналы:

• **YNDX**: 🟢 BUY (сила: 75%)
  └ SMA прорыв + позитивные новости
  
• **FXIT**: 🟡 HOLD (сила: 45%)
  └ Боковое движение, ждем сигнала

🕐 Обновлено: только что
💡 Для реальных сигналов требуется настройка API"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("Команда /signals выполнена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_signals: {e}")
        await update.message.reply_text(f"❌ Ошибка получения сигналов: {str(e)}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — показать статус системы"""
    try:
        logger.info(f"Команда /status от пользователя {update.effective_user.id}")
        
        message = """⚙️ **Статус системы**

🔗 **API подключения:**
• Telegram API: ✅ Работает
• Tinkoff API: ⚠️ Не настроен
• Google Sheets: ⚠️ Не настроен
• OpenAI API: ⚠️ Не настроен

📊 **Функции:**
• Отправка сообщений: ✅ 
• Получение цен: ⚠️ DEMO режим
• Торговые сигналы: ⚠️ DEMO режим
• Логирование: ⚠️ Не настроено

🔧 **Для полной работы настройте:**
1. TINKOFF_SANDBOX_TOKEN в .env
2. OPENAI_API_KEY в .env  
3. SHEETS_WEBHOOK_URL в .env"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("Команда /status выполнена успешно")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_status: {e}")
        await update.message.reply_text(f"❌ Ошибка проверки статуса: {str(e)}")

# ─────────────── запуск ───────────────
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"Ошибка при обработке обновления {update}: {context.error}")

def run_bot() -> None:
    print("🔧 Инициализация бота...")
    print(f"📱 Token: {TOKEN[:10] if TOKEN else 'НЕ НАЙДЕН'}...")
    
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    print(f"💬 Chat ID: {CHAT_ID if CHAT_ID else 'НЕ НАЙДЕН'}")
    
    if not TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
        return
    
    try:
        application = ApplicationBuilder().token(TOKEN).build()
        
        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", cmd_start))
        application.add_handler(CommandHandler("help", cmd_help))
        application.add_handler(CommandHandler("prices", cmd_prices))
        application.add_handler(CommandHandler("signals", cmd_signals))
        application.add_handler(CommandHandler("status", cmd_status))
        
        # Добавляем обработчик ошибок
        application.add_error_handler(error_handler)
        
        print("✅ Бот инициализирован успешно")
        print("🚀 Запуск polling режима...")
        print("📞 Отправьте боту /start для проверки")
        print("🛑 Для остановки: Ctrl+C")
        print("-" * 50)
        
        logger.info("Bot started 🚀 (PTB v20)")
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except Exception as e:
        print(f"❌ ОШИБКА ЗАПУСКА БОТА: {e}")
        logger.error(f"Критическая ошибка: {e}")
        return

# Позволяет запускать:  python daily_plan_bot_ptb.py
if __name__ == "__main__":
    run_bot()
# ==============================================================================