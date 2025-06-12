
#!/usr/bin/env python
import os
import requests
from datetime import datetime
from tinkoff.invest import Client
from signals.sma_breakout import generate_signal

# Переменные окружения
TINKOFF_SANDBOX_TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# FIGI для отслеживания
FIGIS = {
    "BBG004730N88": "YNDX",  # Яндекс
    "BBG00Y91R9T3": "FXIT"   # Fix Price
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
            signal = generate_signal(figi, 'hour')
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

def main():
    """Основная функция бота"""
    try:
        # Получаем цены
        print("📊 Получаем актуальные цены...")
        prices = get_last_prices()
        
        # Получаем сигналы
        print("📈 Анализируем торговые сигналы...")
        signals = get_signals()
        
        # Формируем сообщение
        message = format_message(prices, signals)
        
        # Отправляем или выводим в консоль
        if is_telegram_configured():
            print("📤 Отправляем сообщение в Telegram...")
            if send_telegram_message(message):
                print("✅ Сообщение успешно отправлено!")
            else:
                print("❌ Не удалось отправить в Telegram")
                print("📋 Сообщение:")
                print(message)
        else:
            print("⚠️  Telegram токен или chat_id не настроены/заданы как PLACEHOLDER")
            print("📋 Сообщение:")
            print(message)
            
    except Exception as e:
        print(f"❌ Ошибка выполнения: {e}")

if __name__ == "__main__":
    main()
