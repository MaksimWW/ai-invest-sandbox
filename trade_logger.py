
#!/usr/bin/env python
import os
import datetime as dt
import requests

WEBHOOK = os.getenv("SHEETS_WEBHOOK_URL")
TOKEN = os.getenv("SHEETS_TOKEN")

def log_trade(date: dt.date, ticker: str, figi: str,
              side: str, price: float, qty: int, fees: float = 0):
    """
    Логирует торговую операцию в Google Sheets
    
    Args:
        date: Дата сделки
        ticker: Тикер инструмента (например, YNDX, FXIT)
        figi: FIGI инструмента
        side: Направление сделки ('BUY' или 'SELL')
        price: Цена за единицу
        qty: Количество
        fees: Комиссия (по умолчанию 0)
    
    Returns:
        str: Ответ от Google Sheets скрипта
    
    Raises:
        RuntimeError: Если webhook не настроен
        requests.HTTPError: Если запрос завершился с ошибкой
    """
    if not WEBHOOK or not TOKEN:
        raise RuntimeError("❌ Sheets webhook не настроен! Проверьте SHEETS_WEBHOOK_URL и SHEETS_TOKEN")

    payload = {
        "date": date.isoformat(),   # можно не передавать: Apps Script ставит new Date()
        "ticker": ticker,
        "figi": figi,
        "side": side.upper(),
        "price": price,
        "qty": qty,
        "fees": fees,
        "token": TOKEN
    }
    
    try:
        r = requests.post(WEBHOOK, data=payload, timeout=5)
        r.raise_for_status()          # 200 => OK
        return r.text                 # 'OK' или ошибка из скрипта
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"❌ Ошибка отправки данных в Google Sheets: {e}")

def log_signal_trade(ticker: str, figi: str, signal: str, price: float, qty: int = 1):
    """
    Упрощенная функция для логирования сделок по сигналам бота
    
    Args:
        ticker: Тикер инструмента
        figi: FIGI инструмента
        signal: Торговый сигнал ('BUY', 'SELL', 'HOLD')
        price: Текущая цена
        qty: Количество (по умолчанию 1)
    """
    if signal in ['BUY', 'SELL']:
        try:
            result = log_trade(
                date=dt.date.today(),
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

def test_sheets_connection():
    """Проверяет подключение к Google Sheets"""
    if not WEBHOOK or not TOKEN:
        print("❌ Sheets webhook не настроен!")
        print("Добавьте в .env файл:")
        print("SHEETS_WEBHOOK_URL=ваш_webhook_url")
        print("SHEETS_TOKEN=ваш_токен")
        return False
    
    try:
        # Тестовая запись
        result = log_trade(
            date=dt.date.today(),
            ticker="TEST",
            figi="TEST_FIGI",
            side="BUY",
            price=100.0,
            qty=1,
            fees=0.1
        )
        print(f"✅ Подключение к Google Sheets работает: {result}")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        return False

if __name__ == "__main__":
    # Тест подключения
    test_sheets_connection()
