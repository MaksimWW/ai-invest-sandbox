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

def get_sentiment_score(ticker: str, hours: int = 24, force_refresh: bool = False) -> int:
    """Анализирует настроение новостей по тикеру через LLM с кэшированием"""
    from nlp.sentiment_llm import get_sentiment_score_from_cache, smart_classify
    # from nlp.sentiment import latest_news_ru # remove
    from news_feed import fetch_news
    from nlp.news_rss_async import async_fetch_all
    import asyncio

    # Сначала проверяем кэш (если не принудительное обновление)
    cached_score = get_sentiment_score_from_cache(ticker, hours, force_refresh)
    if cached_score != 0 and not force_refresh:  # Если в кэше есть данные
        print(f"📊 Используем кэшированные данные для {ticker}: {cached_score}")
        return cached_score

    # Если кэш пуст, собираем новые новости и анализируем
    print(f"🔄 Обновляем анализ новостей для {ticker}...")

    # Определяем тип тикера
    russian_tickers = {"YNDX", "FXIT", "GAZP", "LKOH", "SBER", "NVTK"}
    american_tickers = {"NVDA", "AMD", "AAPL", "TSLA", "GOOGL", "MSFT", "META"}

    all_texts = []

    # Мультиязычная агрегация: для всех тикеров пробуем все источники
    if ticker in russian_tickers:
        print(f"🇷🇺 Собираем русские новости {ticker}...")
        from nlp.sentiment import fetch_ru_news
        ru_texts = fetch_ru_news(hours=hours)
        all_texts.extend(ru_texts)

        # Для русских тикеров также пробуем англоязычные источники (международные новости)
        print(f"🌍 Дополнительно ищем международные новости {ticker}...")
        en_texts = fetch_news(ticker, hours=hours)
        all_texts.extend(en_texts)

    elif ticker in american_tickers:
        print(f"🇺🇸 Собираем англоязычные новости {ticker}...")
        en_texts = fetch_news(ticker, hours=hours)
        all_texts.extend(en_texts)

        # Для американских тикеров также пробуем русские источники (возможны международные упоминания)
        print(f"🌍 Дополнительно ищем русские новости {ticker}...")
        from nlp.sentiment import fetch_ru_news
        ru_texts = fetch_ru_news(hours=hours)
        all_texts.extend(ru_texts)

    if not all_texts:
        print(f"❌ Новости для {ticker} не найдены")
        return 0

    # Анализируем каждую новость через LLM с кэшированием
    print(f"🤖 Анализируем {len(all_texts)} новостей через LLM...")

    total_score = 0
    processed = 0

    for text in all_texts:
        try:
            sentiment = smart_classify(text, ticker)
            if sentiment == "positive":
                total_score += 1
            elif sentiment == "negative":
                total_score -= 1
            processed += 1
        except Exception as e:
            print(f"⚠️ Ошибка анализа: {e}")
            continue

    print(f"📊 Настроение {ticker}: {total_score} (из {processed} обработанных новостей)")
    return total_score

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

    # Проверяем, что бот может подключиться к API
    try:
        bot = telebot.TeleBot(TELEGRAM_TOKEN)
        bot.get_me()  # Проверяем соединение
        print("✅ Соединение с Telegram API установлено")
        
        # Простая проверка соединения без сложной логики

        # Проверяем настройку внешних API
        newsapi_key = os.getenv("NEWSAPI_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")

        print("🔑 Настройка внешних API:")
        print(f"   • NewsAPI: {'✅' if newsapi_key else '❌ не настроен'}")
        print(f"   • OpenAI: {'✅' if openai_key else '❌ не настроен'}")

        # Проверяем Redis подключение
        try:
            import redis
            r = redis.Redis(host='0.0.0.0', port=6379, decode_responses=True, socket_timeout=3)
            r.ping()
            print("   • Redis: ✅")
        except Exception as e:
            print(f"   • Redis: ❌ ({e})")
            print("   💡 Бот будет работать без кэширования")

        print("🤖 Telegram бот запущен...")
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
        # print(f"[DEBUG] Получено сообщение: '{text}' от пользователя {msg.from_user.username}")
        # print(f"[DEBUG] Получено сообщение: '{text}' от пользователя {msg.from_user.first_name}")

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
            parts = text.split()
            try:
                fast = int(parts[1]) if len(parts) > 1 else 20
                slow = int(parts[2]) if len(parts) > 2 else 50
                atr  = float(parts[3]) if len(parts) > 3 else 1.0
                interval = parts[4] if len(parts) > 4 else "hour"
                # если указаны тикеры → берём их, иначе все из FIGI_MAP
                tickers = [t.upper() for t in parts[5:]] if len(parts) > 5 else FIGI_MAP.keys()
            except (ValueError, IndexError):
                bot.reply_to(msg,
                    "Формат: /signals FAST SLOW ATR [INTERVAL] [TICKER...]\n"
                    "Пример: /signals 5 15 0.5 15min GAZP LKOH\n"
                    "Интервалы: 1min, 5min, 15min, 30min, hour, day")
                return

            reply = f"📊 Сигналы SMA{fast}/{slow}, ATR≥{atr}, {interval}:\n"
            for tk in tickers:
                figi = FIGI_MAP.get(tk)
                if not figi:
                    reply += f"• {tk:<6} → 🚫 нет FIGI\n"
                    continue
                try:
                    sig = generate_signal(figi,
                                          interval=interval,
                                          fast=fast,
                                          slow=slow,
                                          atr_ratio=atr)
                    reply += f"• {tk:<6} → {sig}\n"
                except Exception as e:
                    reply += f"• {tk:<6} → ⚠️ Ошибка: {e}\n"
            bot.reply_to(msg, reply)
            return

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
/signals [fast] [slow] [ATR] [interval] [ticker...] - торговые сигналы
Пример: /signals 5 15 0.5 15min GAZP LKOH
Интервалы: 1min, 5min, 15min, 30min, hour, day
По умолчанию: /signals = /signals 20 50 1.0 hour (все тикеры)

/sentiment TICKER [hours] - показать последние новости с тональностью
Пример: /sentiment NVDA 24 (новости NVDA за 24 часа)
По умолчанию: /sentiment TICKER = /sentiment TICKER 48 (за 48 часов)

/fresh_news [TICKER] [HOURS] - принудительно обновить новости
Пример: /fresh_news NVDA 12 (обновить новости NVDA за 12 часов)

/ideas [fast] [slow] [ATR] [hours] [ticker...] - композитные идеи (теханализ + новости)
Пример: /ideas 5 15 0.5 6 NVDA AMD  (новости за 6 часов)
По умолчанию: /ideas 5 15 0 24 (все тикеры, новости за 24ч)

/pnl - показать общий P/L
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

        elif text.startswith("/fresh_news"):
            parts = text.split()
            try:
                ticker = parts[1].upper() if len(parts) > 1 else "YNDX"
                hours = int(parts[2]) if len(parts) > 2 else 6
            except (ValueError, IndexError):
                bot.reply_to(msg, "Формат: /fresh_news [TICKER] [HOURS]\nПример: /fresh_news NVDA 12")
                return

            bot.reply_to(msg, f"🔄 Принудительно обновляю новости {ticker} за {hours}ч...")

            try:
                sentiment = get_sentiment_score(ticker, hours=hours, force_refresh=True)
                emoji = "🟢" if sentiment > 0 else "🔴" if sentiment < 0 else "🟡"
                bot.reply_to(msg, f"{emoji} Свежий анализ {ticker}: {sentiment}")
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка обновления: {e}")

        elif text.lower().startswith("/ideas"):
            parts = text.split()
            try:
                # 1-3 аргументы – fast, slow, atr
                fast = int(parts[1]) if len(parts) > 1 else 5
                slow = int(parts[2]) if len(parts) > 2 else 15
                atr = float(parts[3]) if len(parts) > 3 else 0

                # 4-й аргумент (hours) – за сколько часов брать новости
                hours = int(parts[4]) if len(parts) > 4 else 24

                # всё, что после hours – список тикеров
                tickers = [t.upper() for t in parts[5:]] if len(parts) > 5 else list(FIGI_MAP.keys())
            except (ValueError, IndexError):
                bot.reply_to(msg,
                    "Формат: /ideas [fast] [slow] [ATR] [hours] [ticker...]\n"
                    "Пример: /ideas 5 15 0.5 6 NVDA AMD  (новости за 6 часов)\n"
                    "По умолчанию: /ideas 5 15 0 24 (все тикеры, новости за 24ч)")
                return

            reply = f"💡 Композит-идеи SMA{fast}/{slow} ATR≥{atr} новости≤{hours}ч:\n"

            for tk in tickers:
                fg = FIGI_MAP.get(tk)
                if not fg:
                    reply += f"• {tk:<6} → 🚫 нет FIGI\n"
                    continue

                try:
                    signal = generate_signal(fg, fast=fast, slow=slow, atr_ratio=atr)
                    tech = 1 if signal == "BUY" else -1 if signal == "SELL" else 0
                    sent = get_sentiment_score(tk, hours=hours)
                    score = tech + sent
                    if abs(score) >= 2:
                        side = "LONG" if score > 0 else "SHORT"
                        reply += f"• {tk:<6} {side} (score {score})\n"
                except Exception as e:
                    reply += f"• {tk:<6} ⚠️ Ошибка: {e}\n"

            if reply.strip().endswith(":"):
                reply += "Нет сильных идей сейчас."
            bot.reply_to(msg, reply)
            return

        elif text.startswith("/sentiment"):
            parts = text.split()
            if len(parts) < 2:
                bot.reply_to(msg, "Использование: /sentiment TICKER [часов]")
                return
            
            ticker = parts[1].upper()
            try:
                hours = int(parts[2]) if len(parts) > 2 else 48
            except ValueError:
                bot.reply_to(msg, "❌ Неверный формат часов. Используйте число.")
                return
            
            try:
                import sqlite3
                import os
                
                db_path = os.getenv("NEWS_DB", "db/news_cache.db")
                
                # Проверяем существование базы данных
                if not os.path.exists(db_path):
                    bot.reply_to(msg, f"❌ База данных новостей не найдена: {db_path}")
                    return
                
                db = sqlite3.connect(db_path)
                query = """
                  SELECT dt, headline, label
                  FROM   news
                  WHERE  ticker = ? AND dt >= datetime('now', ? || ' hours')
                  ORDER  BY dt DESC
                  LIMIT  5
                """
                rows = db.execute(query, (ticker, -hours)).fetchall()
                db.close()
                
                if not rows:
                    bot.reply_to(msg, f"Новостей по {ticker} за {hours} ч нет.")
                    return
                
                def emoji(lbl):
                    return {1:"👍", -1:"👎", 0:"⚪"}.get(lbl, "❓")
                
                lines = [f"📰 *{ticker}* · {hours}ч\n"]
                for dt_str, hline, lbl in rows:
                    lines.append(f"{emoji(lbl)} {hline[:120]}")   # обрезаем длинные
                
                bot.reply_to(msg, "\n".join(lines), parse_mode="Markdown")
                
            except sqlite3.Error as e:
                bot.reply_to(msg, f"❌ Ошибка базы данных: {e}")
            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка получения новостей: {e}")

        elif text.startswith("/debug"):
            try:
                # Читаем последние 10 строк из лог-файла
                with open("debug_sheets.log", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] if len(lines) > 10 else lines
                    log_content = "".join(last_lines)

                if log_content:
                    bot.reply_to(msg, f"📋 Последние записи лога:\n```\n{log_content}\n```")

            except Exception as e:
                bot.reply_to(msg, f"❌ Ошибка чтения лога: {e}")

        else:
            bot.reply_to(msg, "Неизвестная команда. Используйте /help")

    bot.infinity_polling()

if __name__ == "__main__":
    # Запускаем ежедневный анализ (можно закомментировать)
    # run_daily_analysis()

    # Запускаем Telegram бота
    run_Telegram_bot()