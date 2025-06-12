
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
        "date": date.isoformat(),
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
        r.raise_for_status()
        return r.text
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"❌ Ошибка отправки данных в Google Sheets: {e}")
