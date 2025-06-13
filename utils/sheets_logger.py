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
    # print(f"[DEBUG] log_trade вызвана с параметрами: {ticker}, {side}, {price}, {qty}")

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

    # print("[DEBUG] send to sheets:", payload)

    # Дополнительно логируем в файл для отладки
    import json
    with open("debug_sheets.log", "a", encoding="utf-8") as f:
        f.write(f"[{dt.datetime.now()}] Payload: {json.dumps(payload, ensure_ascii=False)}\n")

    try:
        # print(f"[DEBUG] Отправляем POST запрос на {WEBHOOK}")
        r = requests.post(WEBHOOK, data=payload, timeout=10)
        # print(f"[DEBUG] Получен ответ с кодом: {r.status_code}")

        r.raise_for_status()

        response_text = r.text
        # print(f"[DEBUG] Ответ от сервера: {response_text[:500]}...")

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

def get_pnl() -> float:
    """Запрашивает суммарный P/L у Apps Script."""
    if not WEBHOOK or not TOKEN:
        raise RuntimeError("Sheets webhook not configured")

    url = f"{WEBHOOK}?token={TOKEN}&action=get_pnl"

    try:
        print(f"[DEBUG] Запрашиваем P/L с URL: {url}")
        r = requests.get(url, timeout=10)
        r.raise_for_status()

        print(f"[DEBUG] Ответ: {r.text}")

        if r.text.startswith('AUTH_FAIL'):
            raise RuntimeError('Auth fail from Sheets')

        # Парсим JSON ответ
        try:
            response_data = r.json()
            if "pnl" in response_data:
                return float(response_data["pnl"])
            else:
                raise RuntimeError(f"PNL not found in response: {response_data}")
        except ValueError as e:
            raise RuntimeError(f"Failed to parse JSON response: {r.text}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Network error when requesting PNL: {e}")

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

        # Тестируем получение P/L
        try:
            pnl = get_pnl()
            print(f"✅ Получение P/L работает: {pnl} ₽")
        except Exception as e:
            print(f"⚠️ Ошибка получения P/L: {e}")

        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        return False