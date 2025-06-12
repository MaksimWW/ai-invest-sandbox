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
    print(f"[DEBUG] log_trade вызвана с параметрами: {ticker}, {side}, {price}, {qty}")

    if not WEBHOOK or not TOKEN:
        print("[DEBUG] Ошибка: WEBHOOK или TOKEN не настроены")
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

    print("[DEBUG] send to sheets:", payload)

    # Дополнительно логируем в файл для отладки
    import json
    with open("debug_sheets.log", "a", encoding="utf-8") as f:
        f.write(f"[{dt.datetime.now()}] Payload: {json.dumps(payload, ensure_ascii=False)}\n")

    try:
        print(f"[DEBUG] Отправляем POST запрос на {WEBHOOK}")
        r = requests.post(WEBHOOK, data=payload, timeout=10)
        print(f"[DEBUG] Получен ответ с кодом: {r.status_code}")

        r.raise_for_status()

        response_text = r.text
        print(f"[DEBUG] Ответ от сервера: {response_text[:500]}...")

        # Логируем ответ
        with open("debug_sheets.log", "a", encoding="utf-8") as f:
            f.write(f"[{dt.datetime.now()}] HTTP Status: {r.status_code}\n")
            f.write(f"[{dt.datetime.now()}] Response Headers: {dict(r.headers)}\n")
            f.write(f"[{dt.datetime.now()}] Response Body: {response_text}\n")

        # Проверяем, если ответ содержит HTML (ошибка от Google)
        if response_text.strip().startswith('<!DOCTYPE html>') or '<html>' in response_text:
            # Извлекаем текст ошибки из HTML
            if 'TypeError:' in response_text or 'Error:' in response_text:
                # Ищем различные варианты ошибок
                error_patterns = ['TypeError:', 'ReferenceError:', 'Error:', 'Exception:']
                error_msg = "Неизвестная ошибка"
                
                for pattern in error_patterns:
                    error_start = response_text.find(pattern)
                    if error_start != -1:
                        # Ищем конец ошибки
                        possible_ends = ['</div>', '</span>', '</p>', '\n', '(line']
                        error_end = len(response_text)
                        
                        for end_pattern in possible_ends:
                            end_pos = response_text.find(end_pattern, error_start)
                            if end_pos != -1 and end_pos < error_end:
                                error_end = end_pos
                        
                        error_msg = response_text[error_start:error_end].strip()
                        # Декодируем HTML entities
                        error_msg = error_msg.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', '&')
                        break

                # Специальные сообщения для типичных ошибок
                if 'appendRow' in error_msg:
                    detailed_msg = f"""
🔧 Проблема с Google Apps Script: {error_msg}

Возможные причины:
1. Неправильный ID таблицы Google Sheets в скрипте
2. Лист с именем 'Sheet1' или 'Лист1' не существует
3. У скрипта нет прав доступа к таблице
4. Таблица была удалена или перемещена

Проверьте:
• ID таблицы в коде Google Apps Script
• Имя листа (должно совпадать с реальным)
• Права доступа скрипта к таблице
                    """
                    raise RuntimeError(detailed_msg.strip())
                else:
                    raise RuntimeError(f"❌ Ошибка в Google Apps Script: {error_msg}")

            raise RuntimeError("❌ Google Apps Script вернул HTML страницу с ошибкой. Проверьте настройки скрипта.")

        return response_text

    except requests.exceptions.RequestException as e:
        # Логируем ошибку
        with open("debug_sheets.log", "a", encoding="utf-8") as f:
            f.write(f"[{dt.datetime.now()}] Network Error: {str(e)}\n")
        raise RuntimeError(f"❌ Ошибка сети при отправке данных в Google Sheets: {e}")