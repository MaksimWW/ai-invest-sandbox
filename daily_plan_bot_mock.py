
#!/usr/bin/env python
import os
import requests
import telebot
from datetime import datetime

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# FIGI для отслеживания - mock данные
FIGIS = {
    "BBG004730N88": "YNDX",  # Яндекс
    "BBG00Y91R9T3": "FXIT"   # Fix Price
}

# Обратная карта для поиска FIGI по тикеру
FIGI_MAP = {
    "YNDX": "BBG004730N88",
    "FXIT": "BBG00Y91R9T3",
    "GAZP": "BBG004730RP0",
    "LKOH": "BBG004730ZJ9",
    "SBER": "BBG0047315Y7",   # Сбербанк
    "NVDA": "BBG000BBJQV0",   # NVIDIA
    "AMD":  "BBG000BBQCY0",   # Advanced Micro Devices
}

def get_last_prices():
    """MOCK: Возвращает тестовые цены без обращения к Tinkoff API"""
    print("📊 Используем mock-цены (Tinkoff API отключен)")
    
    # Тестовые цены
    prices = {
        "YNDX": 2510.35,
        "FXIT": 120.45
    }
    
    return prices

def get_signals():
    """MOCK: Возвращает тестовые сигналы"""
    print("📈 Используем mock-сигналы (анализ отключен)")
    
    signals = {
        "YNDX": "BUY",
        "FXIT": "HOLD"
    }
    
    return signals

def format_message(prices, signals):
    """Форматирует сообщение с ценами и сигналами"""
    today = datetime.now().strftime("%Y-%m-%d")
    message = f"📈 План на {today} (DEMO режим)\n"

    for ticker in prices.keys():
        price = prices[ticker]
        signal = signals.get(ticker, "HOLD")

        # Форматируем цену с разделителем тысяч
        formatted_price = f"{price:,.2f}".replace(",", " ")
        message += f"• {ticker}: {formatted_price} ₽\n"
        message += f"  Signal: {signal}\n"

    return message.strip()

def is_telegram_configured():
    """Проверяет, настроен ли Telegram"""
    return (TELEGRAM_TOKEN and TELEGRAM_CHAT_ID and 
            TELEGRAM_TOKEN != "PLACEHOLDER" and 
            TELEGRAM_CHAT_ID != "PLACEHOLDER")

def send_telegram_message(message):
    """Отправляет сообщение в Telegram"""
    if not is_telegram_configured():
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в Telegram: {e}")
        return False

def run_daily_analysis():
    """Запускает ежедневный анализ и отправляет отчет"""
    try:
        print("🤖 Запуск в DEMO режиме (без Tinkoff API)")
        
        # Получаем mock-цены
        print("📊 Получаем тестовые цены...")
        prices = get_last_prices()

        # Получаем mock-сигналы
        print("📈 Генерируем тестовые сигналы...")
        signals = get_signals()

        # Формируем сообщение
        message = format_message(prices, signals)
        message += "\n\n⚠️ DEMO режим: используются тестовые данные"

        # Отправляем или выводим в консоль
        if is_telegram_configured():
            print("📤 Отправляем сообщение в Telegram...")
            if send_telegram_message(message):
                print("✅ Сообщение успешно отправлено!")
            else:
                print("❌ Ошибка отправки. Выводим в консоль:")
                print(message)
        else:
            print("📄 Telegram не настроен. Выводим в консоль:")
            print("\n" + message)

    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")

def run_Telegram_bot():
    """Запускает Telegram бота для обработки команд"""
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "PLACEHOLDER":
        print("❌ TELEGRAM_TOKEN не настроен! Бот не может быть запущен.")
        return

    # Проверяем, что бот может подключиться к API
    try:
        bot = telebot.TeleBot(TELEGRAM_TOKEN)
        bot.get_me()  # Проверяем соединение
        print("✅ Соединение с Telegram API установлено")
        print("🤖 Telegram бот запущен в DEMO режиме...")
    except Exception as e:
        if "409" in str(e):
            print("❌ Ошибка 409: Другой экземпляр бота уже запущен!")
            print("💡 Остановите другие экземпляры и попробуйте снова")
            return
        else:
            print(f"❌ Ошибка подключения к Telegram API: {e}")
            return

    @bot.message_handler(func=lambda message: True)
    def handle_message(msg):
        text = msg.text.strip() if msg.text else ""

        if text.startswith("/prices"):
            try:
                prices = get_last_prices()
                message = "💰 Актуальные цены (DEMO):\n"
                for ticker, price in prices.items():
                    formatted_price = f"{price:,.2f}".replace(",", " ")
                    message += f"• {ticker}: {formatted_price} ₽\n"
                message += "\n⚠️ Тестовые данные"
                bot.reply_to(msg, message)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения цен: {e}")

        elif text.startswith("/signals"):
            try:
                signals = get_signals()
                reply = "📊 Торговые сигналы (DEMO):\n"
                for ticker, signal in signals.items():
                    reply += f"• {ticker:<6} → {signal}\n"
                reply += "\n⚠️ Тестовые данные"
                bot.reply_to(msg, reply)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения сигналов: {e}")

        elif text == "/help":
            help_text = """🤖 Доступные команды (DEMO режим):

/prices - показать тестовые цены
/signals - показать тестовые сигналы
/help - показать эту справку

⚠️ Бот работает в DEMO режиме без реального API"""
            bot.reply_to(msg, help_text)

        else:
            bot.reply_to(msg, "Неизвестная команда. Используйте /help")

    bot.infinity_polling()

if __name__ == "__main__":
    print("🚀 Запуск daily_plan_bot в DEMO режиме")
    print("⚠️ Tinkoff API отключен из-за проблем с библиотеками")
    
    # Запускаем Telegram бота
    run_Telegram_bot()
