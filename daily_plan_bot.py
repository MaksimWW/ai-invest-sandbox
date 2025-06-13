#!/usr/bin/env python
import os
import requests
import telebot
from datetime import datetime
from tinkoff.invest import Client
from signals.sma_breakout import generate_signal
from utils.sheets_logger import log_trade

# Переменные окружения
TINKOFF_SANDBOX_TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# FIGI для отслеживания
FIGIS = {
    "BBG004730N88": "YNDX",  # Яндекс
    "BBG00Y91R9T3": "FXIT"   # Fix Price
}

# Обратная карта для поиска FIGI по тикеру
FIGI_MAP = {ticker: figi for figi, ticker in FIGIS.items()}

def get_last_prices():
    """Получает последние цены акций через Tinkoff Sandbox API"""
    if not TINKOFF_SANDBOX_TOKEN:
        raise RuntimeError("❌ Переменная TINKOFF_SANDBOX_TOKEN не найдена!")

    prices = {}

    with Client(TINKOFF_SANDBOX_TOKEN, app_name="daily-plan-bot") as client:
        for figi, ticker in FIGIS.items():
            try:
                # Получаем последнюю цену через MarketData API
                response = client.market_data.get_last_prices(figi=[figi])
                if response.last_prices:
                    price = response.last_prices[0].price
                    # Конвертируем в рубли
                    price_rub = price.units + price.nano / 1_000_000_000
                    prices[ticker] = price_rub
                else:
                    prices[ticker] = 0.0
            except Exception as e:
                print(f"❌ Ошибка получения цены для {ticker}: {e}")
                prices[ticker] = 0.0

    return prices

def get_signals():
    """Получает торговые сигналы для всех FIGI"""
    signals = {}

    for figi, ticker in FIGIS.items():
        try:
            # Используем настройки по умолчанию: SMA20/50, ATR фильтр 1.0
            signal = generate_signal(figi, 'hour', fast=20, slow=50, atr_ratio=1.0)
            signals[ticker] = signal
        except Exception as e:
            print(f"❌ Ошибка получения сигнала для {ticker}: {e}")
            signals[ticker] = "HOLD"

    return signals

def format_message(prices, signals):
    """Форматирует сообщение с ценами и сигналами"""
    today = datetime.now().strftime("%Y-%m-%d")
    message = f"📈 План на {today}\n"

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

def log_signal_trade(ticker: str, figi: str, signal: str, price: float, qty: int = 1):
    """Упрощенная функция для логирования сделок по сигналам бота"""
    if signal in ['BUY', 'SELL']:
        try:
            result = log_trade(
                date=datetime.now().date(),
                ticker=ticker,
                figi=figi,
                side=signal,
                price=price,
                qty=qty
            )
            print(f"✅ Сделка {signal} {ticker} логирована: {result}")
        except Exception as e:
            print(f"❌ Ошибка логирования сделки {ticker}: {e}")
    else:
        print(f"📝 {ticker}: сигнал {signal} - сделка не выполняется")

def run_daily_analysis():
    """Запускает ежедневный анализ и отправляет отчет"""
    try:
        # Получаем цены
        print("📊 Получаем актуальные цены...")
        prices = get_last_prices()

        # Получаем сигналы
        print("📈 Анализируем торговые сигналы...")
        signals = get_signals()

        # Логируем сделки по сигналам
        print("📝 Логируем торговые сигналы...")
        for figi, ticker in FIGIS.items():
            if ticker in prices and ticker in signals:
                log_signal_trade(ticker, figi, signals[ticker], prices[ticker])

        # Формируем сообщение
        message = format_message(prices, signals)

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

    bot = telebot.TeleBot(TELEGRAM_TOKEN)

    @bot.message_handler(func=lambda message: True)
    def handle_message(msg):
        text = msg.text.strip() if msg.text else ""
        # print(f"[DEBUG] Получено сообщение: '{text}' от пользователя {msg.from_user.username}")
        # print(f"[DEBUG] Получено сообщение: '{text}' от пользователя {msg.from_user.username or msg.from_user.first_name}")

        if text.startswith("/log"):
            parts = text.split()
            if len(parts) != 5:
                bot.reply_to(msg, "Формат: /log BUY|SELL TICKER QTY PRICE")
                return

            _, side, ticker, qty, price = parts
            figi = FIGI_MAP.get(ticker.upper())
            if not figi:
                bot.reply_to(msg, f"FIGI для {ticker} не найден.")
                return

            try:
                # Импортируем функцию здесь, чтобы избежать проблем с областью видимости
                from utils.sheets_logger import log_trade

                # Сначала отправляем подтверждение начала обработки
                bot.reply_to(msg, f"📝 Обрабатываю сделку: {side.upper()} {ticker.upper()} {qty} шт по {price}...")

                # print(f"[DEBUG] Вызываем log_trade для {ticker}")

                resp = log_trade(
                    date=datetime.now().date(),
                    ticker=ticker.upper(),
                    figi=figi,
                    side=side.upper(),
                    price=float(price.replace(',', '.')),
                    qty=int(qty),
                    fees=0
                )
                bot.reply_to(msg, f"✅ записал сделку ({resp})")

                # Дополнительно уведомляем об успехе с деталями
                bot.reply_to(msg, f"📊 Детали: {ticker.upper()} {side.upper()} {qty}x{price} = {int(qty) * float(price.replace(',', '.')):.2f} ₽")

            except Exception as e:
                error_msg = str(e)
                bot.reply_to(msg, f"❌ ошибка записи: {error_msg}")

                # Если это ошибка Google Apps Script, даем конкретные рекомендации
                if "Google Apps Script" in error_msg or "appendRow" in error_msg:
                    bot.reply_to(msg, """
🔧 Проблема с Google Apps Script:
1. Проверьте ID таблицы Google Sheets
2. Убедитесь, что скрипт имеет доступ к таблице
3. Проверьте имя листа (обычно 'Sheet1' или 'Лист1')
4. Убедитесь, что скрипт опубликован как веб-приложение
                    """)
                else:
                    bot.reply_to(msg, f"🔍 Проверьте файл debug_sheets.log для подробностей")

        elif text.startswith("/prices"):
            try:
                prices = get_last_prices()
                message = "💰 Актуальные цены:\n"
                for ticker, price in prices.items():
                    formatted_price = f"{price:,.2f}".replace(",", " ")
                    message += f"• {ticker}: {formatted_price} ₽\n"
                bot.reply_to(msg, message)
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения цен: {e}")

        elif text.lower().startswith("/signals"):
            print(f"[DEBUG] Получена команда /signals: '{text}'")
            parts = text.split()
            try:
                fast = int(parts[1]) if len(parts) > 1 else 20
                slow = int(parts[2]) if len(parts) > 2 else 50
                atr  = float(parts[3]) if len(parts) > 3 else 1.0
                print(f"[DEBUG] Параметры: fast={fast}, slow={slow}, atr={atr}")
            except (IndexError, ValueError) as ve:
                print(f"[DEBUG] Ошибка парсинга параметров: {ve}")
                bot.reply_to(msg, "Формат: /signals [fast] [slow] [ATR]  (напр. /signals 10 40 1.2)")
                return

            try:
                print(f"[DEBUG] Начинаю генерацию сигналов...")
                reply = f"📊 Сигналы SMA{fast}/{slow}, ATR≥{atr}:\n"
                for ticker, figi in FIGI_MAP.items():
                    print(f"[DEBUG] Обрабатываю {ticker} (FIGI: {figi})")
                    sig = generate_signal(figi, interval='hour', fast=fast, slow=slow, atr_ratio=atr)
                    print(f"[DEBUG] Сигнал для {ticker}: {sig}")
                    reply += f"• {ticker:<6} → {sig}\n"
                print(f"[DEBUG] Отправляю ответ: {reply}")
                bot.reply_to(msg, reply)
            except Exception as e:
                print(f"[DEBUG] Ошибка в генерации сигналов: {e}")
                import traceback
                traceback.print_exc()
                bot.reply_to(msg, f"❌ Ошибка получения сигналов: {e}")

        elif text.startswith("/debug"):
            try:
                # Читаем последние 10 строк из лог-файла
                with open("debug_sheets.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) > 10 else lines
                    log_content = "".join(last_lines)

                if log_content:
                    bot.reply_to(msg, f"📋 Последние записи лога:\n```\n{log_content}\n```", parse_mode="Markdown")
                else:
                    bot.reply_to(msg, "📋 Лог-файл пуст")
            except FileNotFoundError:
                bot.reply_to(msg, "📋 Лог-файл не найден")
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка чтения лога: {e}")

        elif text.startswith("/test_sheets"):
            # print(f"[DEBUG] Получена команда: '{text}'")
            bot.reply_to(msg, "🔄 Тестирую подключение к Google Sheets...")

            try:
                from utils.sheets_logger import log_trade
                # print("[DEBUG] Импорт utils.sheets_logger успешен")

                result = log_trade(
                    date=datetime.now().date(),
                    ticker="TEST",
                    figi="TEST_FIGI", 
                    side="BUY",
                    price=100.0,
                    qty=1,
                    fees=0.1
                )

                # print(f"[DEBUG] Результат теста: {result}")
                bot.reply_to(msg, f"✅ Тест Google Sheets успешен!\n📝 Ответ: {result[:200]}...")

            except Exception as e:
                # print(f"[DEBUG] Ошибка теста: {e}")
                bot.reply_to(msg, f"❌ Тест Google Sheets не прошел:\n{str(e)[:500]}...")

        elif text.startswith("/config"):
            # Показываем конфигурацию (без секретов)
            webhook_url = os.getenv("SHEETS_WEBHOOK_URL", "НЕ НАСТРОЕНО")
            token_status = "НАСТРОЕНО" if os.getenv("SHEETS_TOKEN") else "НЕ НАСТРОЕНО"

            config_msg = f"""🔧 Конфигурация Google Sheets:

📡 Webhook URL: {webhook_url[:50]}...
🔑 Token: {token_status}

💡 Для проверки используйте /test_sheets"""

            bot.reply_to(msg, config_msg)

        elif text == "/help":
            help_text = """🤖 Доступные команды:

/log BUY|SELL TICKER QTY PRICE - записать сделку
Пример: /log BUY YNDX 10 2500.50

/prices - показать актуальные цены
/signals - показать торговые сигналы
/debug - показать лог отладки
/config - показать конфигурацию Google Sheets
/test_sheets - проверить подключение к Google Sheets
/help - показать эту справку

Доступные тикеры: YNDX, FXIT"""
            bot.reply_to(msg, help_text)

        elif text.startswith("/pnl"):
             try:
                from utils.sheets_logger import get_pnl
                # print(f"[DEBUG] Запрашиваем P/L с URL: {url}")
                pnl = get_pnl()

                if pnl > 0:
                    emoji = "🟢"
                    status = "Прибыль"
                elif pnl < 0:
                    emoji = "🔴" 
                    status = "Убыток"
                else:
                    emoji = "🟡"
                    status = "В ноль"

                pnl_message = f"""
💰 Текущий P/L

{emoji} {status}: {pnl:,.2f} ₽

📊 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M')}
                """.strip()

                bot.reply_to(msg, pnl_message)

             except Exception as e:
                error_message = f"❌ Ошибка получения P/L: {e}"
                bot.reply_to(msg, error_message)

        elif text.startswith("/debug"):
            try:
                # Читаем последние 10 строк из лог-файла
                with open("debug_sheets.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) > 10 else lines
                    log_content = "".join(last_lines)

                if log_content:
                    bot.reply_to(msg, f"📋 Последние записи лога:\n```\n{log_content}\n```", parse_mode="Markdown")
                else:
                    bot.reply_to(msg, "📋 Лог-файл пуст")
            except FileNotFoundError:
                bot.reply_to(msg, "📋 Лог-файл не найден")
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка чтения лога: {e}")

        elif text == "/help":
            help_text = """🤖 Доступные команды:

/log BUY|SELL TICKER QTY PRICE - записать сделку
Пример: /log BUY YNDX 10 2500.50

/prices - показать актуальные цены
/signals [fast] [slow] [ATR] - торговые сигналы
Пример: /signals 10 40 1.2 (SMA10/40, ATR≥1.2)
По умолчанию: /signals = /signals 20 50 1.0

/pnl - показать общий P/L
/debug - показать лог отладки
/config - показать конфигурацию Google Sheets
/test_sheets - проверить подключение к Google Sheets
/help - показать эту справку

Доступные тикеры: YNDX, FXIT"""
            bot.reply_to(msg, help_text)

        else:
            bot.reply_to(msg, "❓ Неизвестная команда. Используйте /help для справки")

    print("🤖 Telegram бот запущен...")
    bot.polling(none_stop=True)

def main():
    """Основная функция - выбор режима работы"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "bot":
        # Режим Telegram бота
        run_Telegram_bot()
    else:
        # Режим разового анализа
        run_daily_analysis()

if __name__ == "__main__":
    main()