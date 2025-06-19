# ==== python-telegram-bot v20 =================================================
import os, logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from tinkoff_api import get_prices_with_fallback, check_api_connection, format_price_change

TOKEN = os.getenv("TELEGRAM_TOKEN")  # возьмёт из Secrets

# Настраиваем красивое логирование
logging.basicConfig(
    format="%(asctime)s │ %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S"
)

# Отключаем избыточные HTTP логи
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ──────────────── ХЭНДЛЕРЫ ────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start — приветствие и краткая справка"""
    try:
        logger.info("🚀 /start - запуск бота")
        
        message = """🤖 **AI Invest PlanBot запущен!**

📊 Доступные команды:
• /help - полная справка по командам
• /prices - текущие цены акций
• /signals - торговые сигналы  
• /status - статус системы

💡 Отправьте /help для подробной информации!"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("✅ /start - выполнено")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_start: {e}")
        await update.message.reply_text("❌ Произошла ошибка при выполнении команды /start")

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help — справка по командам"""
    try:
        logger.info("❓ /help - справка по командам")
        
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
        logger.info("✅ /help - выполнено")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_help: {e}")
        await update.message.reply_text("❌ Произошла ошибка при выполнении команды /help")

async def cmd_prices(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/prices — показать текущие цены акций"""
    try:
        logger.info("📈 /prices - запрос цен акций")
        
        # Получаем цены через новый модуль
        prices = get_prices_with_fallback()
        api_connected = check_api_connection()
        
        if api_connected:
            mode_text = "✅ Реальные данные Tinkoff API"
        else:
            mode_text = "⚠️ DEMO режим - тестовые данные"
        
        # Формируем сообщение
        message = f"📈 **Текущие цены акций**\n\n{mode_text}:\n\n"
        
        for ticker, price in prices.items():
            change_icon = format_price_change(price, demo_mode=not api_connected)
            message += f"• **{ticker}**: {price:,.2f} ₽ {change_icon}\n"
        
        message += f"\n🕐 Обновлено: только что"
        
        if not api_connected:
            message += "\n💡 Для реальных данных настройте TINKOFF_SANDBOX_TOKEN"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("✅ /prices - отправлены")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_prices: {e}")
        await update.message.reply_text(f"❌ Ошибка получения цен: {str(e)}")

async def cmd_signals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/signals — показать торговые сигналы"""
    try:
        logger.info("📊 /signals - запрос торговых сигналов")
        
        # Получаем реальные сигналы
        from signals.sma_breakout import generate_signal
        
        api_connected = check_api_connection()
        mode_text = "✅ Реальные SMA сигналы" if api_connected else "⚠️ DEMO режим"
        
        message = f"📊 **Торговые сигналы (SMA 20/50)**\n\n{mode_text}:\n\n"
        
        # Генерируем сигналы для основных тикеров
        main_tickers = ["YNDX", "FXIT", "GAZP", "SBER"]
        
        for ticker in main_tickers:
            figi = FIGI_MAP.get(ticker)
            if figi:
                try:
                    signal = generate_signal(figi, interval='hour', fast=20, slow=50)
                    signal_emoji = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}.get(signal, "⚪")
                    
                    signal_desc = {
                        "BUY": "SMA20 пересекла SMA50 ↗️",
                        "SELL": "SMA20 пересекла SMA50 ↘️", 
                        "HOLD": "Боковое движение, нет пересечения"
                    }.get(signal, "Неизвестный сигнал")
                    
                    message += f"• **{ticker}**: {signal_emoji} {signal}\n"
                    message += f"  └ {signal_desc}\n\n"
                    
                except Exception as e:
                    message += f"• **{ticker}**: ❌ Ошибка анализа\n\n"
                    logger.error(f"Ошибка сигнала {ticker}: {e}")
        
        message += f"🕐 Обновлено: только что\n"
        message += f"📈 Интервал: часовые свечи\n"
        message += f"📊 Индикатор: SMA(20) vs SMA(50)"
        
        if not api_connected:
            message += "\n💡 Для реальных данных настройте TINKOFF_SANDBOX_TOKEN"
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("✅ /signals - отправлены")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_signals: {e}")
        await update.message.reply_text(f"❌ Ошибка получения сигналов: {str(e)}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/status — показать статус системы"""
    try:
        logger.info("⚙️ /status - проверка статуса системы")
        
        # Проверяем статус Tinkoff API
        tinkoff_status = "✅ Работает" if check_api_connection() else "⚠️ Не настроен"
        tinkoff_token = "✅ Настроен" if os.getenv("TINKOFF_SANDBOX_TOKEN") else "❌ Отсутствует"
        
        # Проверяем другие переменные окружения
        openai_key = "✅ Настроен" if os.getenv("OPENAI_API_KEY") else "❌ Отсутствует"
        sheets_url = "✅ Настроен" if os.getenv("SHEETS_WEBHOOK_URL") else "❌ Отсутствует"
        
        message = f"""⚙️ **Статус системы**

🔗 **API подключения:**
• Telegram API: ✅ Работает
• Tinkoff API: {tinkoff_status}
• Google Sheets: ⚠️ Не настроен
• OpenAI API: ⚠️ Не настроен

🔑 **Токены и ключи:**
• TINKOFF_SANDBOX_TOKEN: {tinkoff_token}
• OPENAI_API_KEY: {openai_key}
• SHEETS_WEBHOOK_URL: {sheets_url}

📊 **Функции:**
• Отправка сообщений: ✅ 
• Получение цен: {'✅ Реальные данные' if check_api_connection() else '⚠️ DEMO режим'}
• Торговые сигналы: ⚠️ DEMO режим
• Логирование: ⚠️ Не настроено

🔧 **Для полной работы настройте:**
1. TINKOFF_SANDBOX_TOKEN в .env
2. OPENAI_API_KEY в .env  
3. SHEETS_WEBHOOK_URL в .env"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
        logger.info("✅ /status - отправлен")
        
    except Exception as e:
        logger.error(f"Ошибка в cmd_status: {e}")
        await update.message.reply_text(f"❌ Ошибка проверки статуса: {str(e)}")

# ─────────────── запуск ───────────────
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик ошибок"""
    logger.error(f"❌ Ошибка: {context.error}")

def check_and_stop_other_bots():
    """Проверяет и останавливает другие экземпляры бота"""
    import psutil
    import time
    
    print("🔍 Проверка других экземпляров бота...")
    
    current_pid = os.getpid()
    killed_count = 0
    
    bot_files = [
        'daily_plan_bot_ptb.py',
        'daily_plan_bot.py', 
        'daily_plan_bot_fixed.py',
        'daily_plan_bot_mock.py'
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue  # Пропускаем текущий процесс
                
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                if 'python' in cmdline[0].lower():
                    for bot_file in bot_files:
                        if any(bot_file in cmd for cmd in cmdline):
                            print(f"🔴 Найден другой экземпляр: PID {proc.info['pid']}")
                            try:
                                proc.terminate()
                                proc.wait(timeout=3)
                                print(f"✅ Экземпляр {proc.info['pid']} остановлен")
                                killed_count += 1
                            except psutil.TimeoutExpired:
                                proc.kill()
                                print(f"🔥 Экземпляр {proc.info['pid']} принудительно завершен")
                                killed_count += 1
                            except Exception as e:
                                print(f"❌ Ошибка остановки: {e}")
                            break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if killed_count > 0:
        print(f"🛑 Остановлено экземпляров: {killed_count}")
        print("⏱️ Ждем 3 секунды...")
        time.sleep(3)
    else:
        print("✅ Других экземпляров не найдено")

def run_bot() -> None:
    print("🚀 Запуск Telegram-бота (PTB v20)")
    print("🔧 Инициализация бота...")
    print(f"📱 Token: {TOKEN[:10] if TOKEN else 'НЕ НАЙДЕН'}...")
    
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
    print(f"💬 Chat ID: {CHAT_ID if CHAT_ID else 'НЕ НАЙДЕН'}")
    
    if not TOKEN:
        print("❌ ОШИБКА: TELEGRAM_TOKEN не найден в переменных окружения!")
        return
    
    # Останавливаем другие экземпляры перед запуском
    try:
        check_and_stop_other_bots()
    except Exception as e:
        print(f"⚠️ Ошибка при проверке других экземпляров: {e}")
    
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
        
        logger.info("🤖 Бот запущен и готов к работе")
        application.run_polling(allowed_updates=["message", "callback_query"])
        
    except Exception as e:
        error_msg = str(e)
        if "Conflict: terminated by other getUpdates request" in error_msg:
            print("❌ КОНФЛИКТ: Обнаружен другой экземпляр бота!")
            print("🔧 Попробуйте запустить: python stop_all_bots.py")
            print("🔄 Затем перезапустите бота")
        else:
            print(f"❌ ОШИБКА ЗАПУСКА БОТА: {e}")
        logger.error(f"Критическая ошибка: {e}")
        return

# Позволяет запускать:  python daily_plan_bot_ptb.py
if __name__ == "__main__":
    run_bot()
# ==============================================================================