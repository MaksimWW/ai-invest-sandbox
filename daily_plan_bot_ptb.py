
#!/usr/bin/env python
import os
import requests
import telebot
from datetime import datetime
import sys

# Переменные окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
TINKOFF_TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")

# Добавляем модули
sys.path.append('nlp')
sys.path.append('signals')

# FIGI для отслеживания
FIGI_MAP = {
    "YNDX": "BBG004730N88",
    "FXIT": "BBG00Y91R9T3",
    "GAZP": "BBG004730RP0",
    "LKOH": "BBG004730ZJ9",
    "SBER": "BBG0047315Y7",
}

def get_tinkoff_prices():
    """Получает цены через REST API Tinkoff без grpc"""
    if not TINKOFF_TOKEN:
        print("⚠️ TINKOFF_TOKEN не настроен, используем mock-данные")
        return {
            "YNDX": 2510.35,
            "FXIT": 120.45,
            "GAZP": 180.20,
            "SBER": 250.15
        }
    
    print("📊 Получаем цены через Tinkoff REST API...")
    prices = {}
    
    # REST API endpoint для получения цен
    base_url = "https://invest-public-api.tinkoff.ru/rest"
    headers = {
        "Authorization": f"Bearer {TINKOFF_TOKEN}",
        "Content-Type": "application/json"
    }
    
    for ticker, figi in FIGI_MAP.items():
        try:
            # Запрос последней цены
            url = f"{base_url}/tinkoff.public.invest.api.contract.v1.MarketDataService/GetLastPrices"
            payload = {
                "figi": [figi]
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                last_prices = data.get("lastPrices", [])
                
                if last_prices:
                    price_data = last_prices[0]
                    price = price_data.get("price", {})
                    # Цена в формате units.nano
                    units = price.get("units", 0)
                    nano = price.get("nano", 0)
                    final_price = float(units) + float(nano) / 1_000_000_000
                    
                    prices[ticker] = final_price
                    print(f"   ✅ {ticker}: {final_price:.2f} ₽")
                else:
                    print(f"   ❌ {ticker}: Нет данных")
                    
        except Exception as e:
            print(f"   ❌ {ticker}: Ошибка - {e}")
    
    # Если не удалось получить цены, используем mock
    if not prices:
        print("⚠️ Не удалось получить цены, используем mock-данные")
        prices = {
            "YNDX": 2510.35,
            "FXIT": 120.45,
            "GAZP": 180.20,
            "SBER": 250.15
        }
    
    return prices

def get_sentiment_score(ticker, hours=24):
    """Получает sentiment score для тикера"""
    try:
        from sentiment_llm import analyze_sentiment_for_ticker
        return analyze_sentiment_for_ticker(ticker, hours)
    except Exception as e:
        print(f"⚠️ Ошибка sentiment: {e}")
        return 0  # Нейтральный sentiment

def get_signals():
    """Генерирует торговые сигналы на основе цен и sentiment"""
    try:
        from composite import generate_composite_signals
        prices = get_tinkoff_prices()
        
        # Получаем sentiment для каждого тикера
        sentiment_scores = {}
        for ticker in prices.keys():
            sentiment_scores[ticker] = get_sentiment_score(ticker, 48)
        
        signals = generate_composite_signals(prices, sentiment_scores)
        return signals
        
    except Exception as e:
        print(f"⚠️ Ошибка генерации сигналов: {e}")
        # Fallback сигналы
        return {
            "YNDX": "HOLD",
            "FXIT": "BUY",
            "GAZP": "HOLD",
            "SBER": "SELL"
        }

def format_message(prices, signals):
    """Форматирует сообщение с ценами и сигналами"""
    today = datetime.now().strftime("%Y-%m-%d")
    message = f"📈 План на {today}\n"

    for ticker in prices.keys():
        price = prices[ticker]
        signal = signals.get(ticker, "HOLD")
        
        # Эмодзи для сигналов
        signal_emoji = {
            "BUY": "🟢",
            "SELL": "🔴", 
            "HOLD": "🟡"
        }.get(signal, "⚪")

        formatted_price = f"{price:,.2f}".replace(",", " ")
        message += f"• {ticker}: {formatted_price} ₽ {signal_emoji} {signal}\n"

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
        print("🤖 Запуск ежедневного анализа...")
        
        print("📊 Получаем цены...")
        prices = get_tinkoff_prices()

        print("📈 Генерируем сигналы...")
        signals = get_signals()

        message = format_message(prices, signals)

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

def run_telegram_bot():
    """Запускает Telegram бота для обработки команд"""
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "PLACEHOLDER":
        print("❌ TELEGRAM_TOKEN не настроен! Бот не может быть запущен.")
        return

    try:
        bot = telebot.TeleBot(TELEGRAM_TOKEN)
        bot.get_me()
        print("✅ Соединение с Telegram API установлено")
        print("🤖 Telegram бот запущен...")
    except Exception as e:
        if "409" in str(e):
            print("❌ Ошибка 409: Другой экземпляр бота уже запущен!")
            return
        else:
            print(f"❌ Ошибка подключения к Telegram API: {e}")
            return

    @bot.message_handler(func=lambda message: True)
    def handle_message(msg):
        text = msg.text.strip() if msg.text else ""

        if text.startswith("/prices"):
            try:
                prices = get_tinkoff_prices()
                message = "💰 Актуальные цены:\n"
                for ticker, price in prices.items():
                    formatted_price = f"{price:,.2f}".replace(",", " ")
                    message += f"• {ticker}: {formatted_price} ₽\n"
                bot.reply_to(msg, message)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения цен: {e}")

        elif text.startswith("/signals"):
            try:
                signals = get_signals()
                reply = "📊 Торговые сигналы:\n"
                for ticker, signal in signals.items():
                    signal_emoji = {
                        "BUY": "🟢",
                        "SELL": "🔴", 
                        "HOLD": "🟡"
                    }.get(signal, "⚪")
                    reply += f"• {ticker:<6} → {signal_emoji} {signal}\n"
                bot.reply_to(msg, reply)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения сигналов: {e}")

        elif text == "/analysis":
            try:
                prices = get_tinkoff_prices()
                signals = get_signals()
                message = format_message(prices, signals)
                bot.reply_to(msg, message)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка анализа: {e}")

        elif text == "/help":
            help_text = """🤖 Доступные команды:

/prices - показать актуальные цены
/signals - показать торговые сигналы  
/analysis - полный анализ с ценами и сигналами
/help - показать эту справку"""
            bot.reply_to(msg, help_text)

        else:
            bot.reply_to(msg, "Неизвестная команда. Используйте /help")

    bot.infinity_polling()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "analysis":
        run_daily_analysis()
    else:
        print("🚀 Запуск daily_plan_bot (исправленная версия)")
        run_telegram_bot()
