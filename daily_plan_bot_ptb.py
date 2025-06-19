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
    """/start — приветствие и краткая справка"""
    message = """🤖 **AI Invest PlanBot запущен!**

📊 Доступные команды:
• /help - полная справка по командам
• /prices - текущие цены акций
• /signals - торговые сигналы  
• /status - статус системы

💡 Отправьте /help для подробной информации!"""
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — справка по командам"""
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

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/prices — показать текущие цены акций"""
    try:
        message = """📈 **Текущие цены акций**

⚠️ DEMO режим - тестовые данные:

• **YNDX**: 2,450.50 ₽ 📈 (+1.2%)
• **FXIT**: 1,180.25 ₽ 📉 (-0.8%)

🕐 Обновлено: только что
💡 Для реальных данных требуется настройка Tinkoff API"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения цен: {str(e)}")

async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/signals — показать торговые сигналы"""
    try:
        message = """📊 **Торговые сигналы**

⚠️ DEMO режим - тестовые сигналы:

• **YNDX**: 🟢 BUY (сила: 75%)
  └ SMA прорыв + позитивные новости
  
• **FXIT**: 🟡 HOLD (сила: 45%)
  └ Боковое движение, ждем сигнала

🕐 Обновлено: только что
💡 Для реальных сигналов требуется настройка API"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка получения сигналов: {str(e)}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — показать статус системы"""
    try:
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
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка проверки статуса: {str(e)}")

# ─────────────── запуск ───────────────
def run_bot() -> None:
    print("🔧 Инициализация бота...")
    print(f"📱 Token: {TOKEN[:10] if TOKEN else 'НЕ НАЙДЕН'}...")
    
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
        
        print("✅ Бот инициализирован успешно")
        print("🚀 Запуск polling режима...")
        print("📞 Отправьте боту /start для проверки")
        print("🛑 Для остановки: Ctrl+C")
        print("-" * 50)
        
        logger.info("Bot started 🚀 (PTB v20)")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ ОШИБКА ЗАПУСКА БОТА: {e}")
        return

# Позволяет запускать:  python daily_plan_bot_ptb.py
if __name__ == "__main__":
    run_bot()
# ==============================================================================