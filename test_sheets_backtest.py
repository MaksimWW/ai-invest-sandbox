
#!/usr/bin/env python
"""
🔍 Пошаговый тест отправки данных бэктеста в Google Sheets
"""

import os
import requests
import json
import datetime as dt
from dotenv import load_dotenv

def step1_check_config():
    """Шаг 1: Проверка конфигурации"""
    print("🔍 ШАГ 1: ПРОВЕРКА КОНФИГУРАЦИИ")
    print("=" * 50)
    
    load_dotenv()
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    if not webhook_url:
        print("❌ SHEETS_WEBHOOK_URL не найден")
        return False
    
    if not token:
        print("❌ SHEETS_TOKEN не найден")
        return False
    
    print(f"✅ URL: {webhook_url[:50]}...")
    print(f"✅ Token: {token[:10]}...")
    return True

def step2_test_simple_ping():
    """Шаг 2: Простой ping тест"""
    print("\n🔍 ШАГ 2: ПРОСТОЙ PING ТЕСТ")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    payload = {
        "token": token,
        "test": "ping"
    }
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ Webhook доступен")
            return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def step3_test_single_backtest_row():
    """Шаг 3: Тест одной строки бэктеста"""
    print("\n🔍 ШАГ 3: ТЕСТ ОДНОЙ СТРОКИ БЭКТЕСТА")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    # Одна тестовая строка бэктеста
    test_row = [
        "TEST",  # ticker
        5,       # N (total)
        3,       # pos
        1,       # neg
        1,       # neu
        2,       # PnL
        dt.datetime.utcnow().isoformat(timespec="seconds")
    ]
    
    payload = {
        "token": token,
        "tag": "backtest",
        "rows": [test_row]
    }
    
    print(f"📤 Отправляем: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Тестовая строка бэктеста отправлена успешно")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def step4_test_real_backtest_data():
    """Шаг 4: Тест реальных данных бэктеста"""
    print("\n🔍 ШАГ 4: ТЕСТ РЕАЛЬНЫХ ДАННЫХ БЭКТЕСТА")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    # Получаем реальные данные из SQLite
    import sqlite3
    import collections
    
    DB = os.getenv("NEWS_DB", "db/news_cache.db")
    
    try:
        conn = sqlite3.connect(DB)
        rows = conn.execute("SELECT ticker,label FROM news").fetchall()
        print(f"📊 Найдено записей в БД: {len(rows)}")
        
        if not rows:
            print("⚠️ Нет данных для бэктеста")
            return False
        
        # Анализируем данные
        stats = collections.defaultdict(lambda: {"pos":0,"neg":0,"neu":0})
        for ticker, label in rows:
            if label > 0:   stats[ticker]["pos"] += 1
            elif label < 0: stats[ticker]["neg"] += 1
            else:           stats[ticker]["neu"] += 1
        
        # Формируем строки для отправки
        backtest_rows = []
        timestamp = dt.datetime.utcnow().isoformat(timespec="seconds")
        
        for ticker, data in stats.items():
            data["N"] = data["pos"] + data["neg"] + data["neu"]
            data["PnL"] = data["pos"] - data["neg"]
            
            row = [
                ticker,
                data["N"],
                data["pos"],
                data["neg"],
                data["neu"],
                data["PnL"],
                timestamp
            ]
            backtest_rows.append(row)
        
        print(f"📋 Подготовлено строк: {len(backtest_rows)}")
        for row in backtest_rows:
            print(f"   {row}")
        
        payload = {
            "token": token,
            "tag": "backtest",
            "rows": backtest_rows
        }
        
        response = requests.post(webhook_url, json=payload, timeout=15)
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Реальные данные бэктеста отправлены успешно")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    """Основная функция теста"""
    print("🧪 ПОШАГОВЫЙ ТЕСТ ОТПРАВКИ БЭКТЕСТА В GOOGLE SHEETS")
    print("=" * 60)
    
    # Шаг 1: Конфигурация
    if not step1_check_config():
        print("\n❌ ТЕСТ ОСТАНОВЛЕН: Проблемы с конфигурацией")
        return
    
    # Шаг 2: Ping тест
    if not step2_test_simple_ping():
        print("\n❌ ТЕСТ ОСТАНОВЛЕН: Webhook недоступен")
        return
    
    # Шаг 3: Тест одной строки
    if not step3_test_single_backtest_row():
        print("\n❌ ТЕСТ ОСТАНОВЛЕН: Проблемы с отправкой данных")
        return
    
    # Шаг 4: Тест реальных данных
    if not step4_test_real_backtest_data():
        print("\n❌ ТЕСТ ОСТАНОВЛЕН: Проблемы с реальными данными")
        return
    
    print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("🎯 Данные бэктеста должны появиться в Google Sheets")

if __name__ == "__main__":
    main()
