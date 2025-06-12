
#!/usr/bin/env python
"""
🔍 ПОШАГОВАЯ ДИАГНОСТИКА GOOGLE SHEETS
====================================
Тестируем каждый компонент отдельно для выявления проблемы
"""

import os
import sys
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

def step1_check_environment():
    """Шаг 1: Проверка переменных окружения"""
    print("🔍 ШАГ 1: ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ")
    print("=" * 50)
    
    load_dotenv()
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    print(f"📡 SHEETS_WEBHOOK_URL: {webhook_url if webhook_url else '❌ НЕ НАЙДЕН'}")
    print(f"🔑 SHEETS_TOKEN: {token if token else '❌ НЕ НАЙДЕН'}")
    
    if not webhook_url or not token:
        print("\n❌ ОШИБКА: Переменные окружения не настроены!")
        print("Добавьте в .env файл:")
        print("SHEETS_WEBHOOK_URL=https://script.google.com/macros/s/YOUR_SCRIPT_ID/exec")
        print("SHEETS_TOKEN=mySecret123")
        return False
    
    # Проверяем формат URL
    if not webhook_url.startswith("https://script.google.com/macros/s/"):
        print("⚠️  ПРЕДУПРЕЖДЕНИЕ: URL не похож на Google Apps Script webhook")
        print("   Ожидаемый формат: https://script.google.com/macros/s/SCRIPT_ID/exec")
    
    print("✅ Переменные окружения в порядке")
    return True

def step2_test_network_connection():
    """Шаг 2: Проверка сетевого подключения"""
    print("\n🔍 ШАГ 2: ПРОВЕРКА СЕТЕВОГО ПОДКЛЮЧЕНИЯ")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    
    try:
        print("📡 Проверяем доступность URL...")
        response = requests.get(webhook_url, timeout=10)
        print(f"✅ URL доступен (статус: {response.status_code})")
        return True
    except requests.exceptions.Timeout:
        print("❌ Таймаут - URL не отвечает")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения - проверьте интернет")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def step3_test_simple_post():
    """Шаг 3: Простой POST запрос"""
    print("\n🔍 ШАГ 3: ТЕСТ ПРОСТОГО POST ЗАПРОСА")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    # Простейший payload
    simple_payload = {
        "test": "hello",
        "token": token
    }
    
    try:
        print("📤 Отправляем простой POST запрос...")
        print(f"📋 Payload: {simple_payload}")
        
        response = requests.post(
            webhook_url,
            data=simple_payload,
            timeout=15,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ POST запрос выполнен успешно")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка POST запроса: {e}")
        return False

def step4_test_ping_endpoint():
    """Шаг 4: Тест ping endpoint"""
    print("\n🔍 ШАГ 4: ТЕСТ PING ENDPOINT")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    ping_payload = {
        "test": "ping",
        "token": token
    }
    
    try:
        print("📤 Отправляем ping запрос...")
        response = requests.post(webhook_url, data=ping_payload, timeout=15)
        
        print(f"📊 HTTP Status: {response.status_code}")
        response_text = response.text.strip()
        print(f"📄 Response: {response_text}")
        
        # Анализируем ответ
        if response_text.startswith('<!DOCTYPE html>'):
            print("❌ Получен HTML вместо JSON - ошибка в скрипте")
            analyze_html_error(response_text)
            return False
        
        try:
            json_response = json.loads(response_text)
            if json_response.get("ok") == True:
                print("✅ Ping endpoint работает!")
                return True
            else:
                print(f"❌ Ping failed: {json_response}")
                return False
        except json.JSONDecodeError:
            print(f"⚠️  Неожиданный формат ответа: {response_text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка ping запроса: {e}")
        return False

def step5_test_data_write():
    """Шаг 5: Тест записи данных"""
    print("\n🔍 ШАГ 5: ТЕСТ ЗАПИСИ ДАННЫХ В ТАБЛИЦУ")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    # Минимальный payload для записи
    write_payload = {
        "date": "2025-06-12",
        "ticker": "DEBUG_TEST",
        "figi": "DEBUG_FIGI",
        "side": "BUY",
        "price": "99.99",
        "qty": "1",
        "fees": "0.0",
        "token": token
    }
    
    try:
        print("📤 Отправляем данные для записи...")
        print(f"📋 Payload: {write_payload}")
        
        response = requests.post(webhook_url, data=write_payload, timeout=20)
        
        print(f"📊 HTTP Status: {response.status_code}")
        response_text = response.text.strip()
        print(f"📄 Response: {response_text[:300]}...")
        
        # Детальный анализ ответа
        if response_text.startswith('<!DOCTYPE html>'):
            print("❌ Получен HTML - ошибка при записи в таблицу")
            analyze_html_error(response_text)
            return False
        
        try:
            json_response = json.loads(response_text)
            if json_response.get("ok") == True:
                print("✅ Запись в таблицу успешна!")
                print(f"✅ Данные записаны: {json_response.get('data', 'N/A')}")
                return True
            else:
                print(f"❌ Ошибка записи: {json_response.get('error', 'Unknown')}")
                return False
        except json.JSONDecodeError:
            if response_text == "OK":
                print("✅ Получен ответ 'OK' - запись успешна!")
                return True
            else:
                print(f"⚠️  Неожиданный формат ответа: {response_text}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка записи данных: {e}")
        return False

def step6_test_multiple_requests():
    """Шаг 6: Тест множественных запросов"""
    print("\n🔍 ШАГ 6: ТЕСТ МНОЖЕСТВЕННЫХ ЗАПРОСОВ")
    print("=" * 50)
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    success_count = 0
    test_count = 3
    
    for i in range(test_count):
        print(f"\n📤 Запрос {i+1}/{test_count}...")
        
        payload = {
            "date": "2025-06-12",
            "ticker": f"TEST_{i+1}",
            "figi": f"TEST_FIGI_{i+1}",
            "side": "BUY" if i % 2 == 0 else "SELL",
            "price": str(100.0 + i),
            "qty": "1",
            "fees": "0.1",
            "token": token
        }
        
        try:
            response = requests.post(webhook_url, data=payload, timeout=15)
            
            if response.status_code == 200 and not response.text.startswith('<!DOCTYPE html>'):
                print(f"✅ Запрос {i+1} успешен")
                success_count += 1
            else:
                print(f"❌ Запрос {i+1} неудачен: {response.text[:100]}...")
                
        except Exception as e:
            print(f"❌ Запрос {i+1} ошибка: {e}")
    
    print(f"\n📊 Результат: {success_count}/{test_count} запросов успешны")
    return success_count == test_count

def analyze_html_error(html_text):
    """Анализирует HTML ошибку от Google Apps Script"""
    print("\n🔍 АНАЛИЗ HTML ОШИБКИ:")
    print("-" * 30)
    
    # Ищем текст ошибки
    if 'TypeError:' in html_text:
        start = html_text.find('TypeError:')
        end = html_text.find('</div>', start)
        if end == -1:
            end = html_text.find('(line', start)
        if end != -1:
            error_text = html_text[start:end].strip()
            # Декодируем HTML entities
            error_text = error_text.replace('&#39;', "'").replace('&quot;', '"').replace('&amp;', '&')
            print(f"🚨 Ошибка: {error_text}")
    
    # Специфичные проверки
    if 'openById' in html_text:
        print("\n💡 ПРОБЛЕМА: Неправильный ID таблицы Google Sheets")
        print("🔧 РЕШЕНИЕ:")
        print("1. Откройте вашу Google Sheets таблицу")
        print("2. Скопируйте ID из URL: docs.google.com/spreadsheets/d/ID_ЗДЕСЬ/edit")
        print("3. Замените SPREADSHEET_ID в Google Apps Script на правильный ID")
        
    elif 'appendRow' in html_text:
        print("\n💡 ПРОБЛЕМА: Ошибка при записи в лист")
        print("🔧 РЕШЕНИЕ:")
        print("1. Проверьте имя листа (Sheet1, Лист1)")
        print("2. Убедитесь, что лист существует")
        print("3. Проверьте права доступа скрипта к таблице")
        
    elif 'getActiveSheet' in html_text:
        print("\n💡 ПРОБЛЕМА: Ошибка доступа к листу")
        print("🔧 РЕШЕНИЕ:")
        print("1. Используйте getSheetByName('Sheet1') вместо getActiveSheet()")
        print("2. Убедитесь, что лист с таким именем существует")

def show_troubleshooting_guide():
    """Показывает руководство по устранению неполадок"""
    print("\n" + "=" * 60)
    print("🛠️  РУКОВОДСТВО ПО УСТРАНЕНИЮ НЕПОЛАДОК")
    print("=" * 60)
    
    print("\n📋 ЧАСТЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:")
    print("-" * 40)
    
    problems = [
        {
            "problem": "TypeError: Cannot read properties of null (reading 'appendRow')",
            "solutions": [
                "Неправильный ID таблицы Google Sheets",
                "Замените SPREADSHEET_ID в скрипте на правильный",
                "ID берется из URL таблицы: docs.google.com/spreadsheets/d/ID_ЗДЕСЬ/edit"
            ]
        },
        {
            "problem": "HTML ответ вместо JSON",
            "solutions": [
                "Ошибка в коде Google Apps Script",
                "Проверьте синтаксис JavaScript в скрипте",
                "Убедитесь, что скрипт опубликован как веб-приложение"
            ]
        },
        {
            "problem": "Таймаут или сетевые ошибки",
            "solutions": [
                "Проверьте интернет подключение",
                "Убедитесь, что URL скрипта правильный",
                "Попробуйте переопубликовать скрипт"
            ]
        }
    ]
    
    for i, item in enumerate(problems, 1):
        print(f"\n{i}. 🚨 {item['problem']}")
        for solution in item['solutions']:
            print(f"   • {solution}")
    
    print(f"\n📚 ПОЛЕЗНЫЕ ССЫЛКИ:")
    print("• Google Apps Script: https://script.google.com")
    print("• Google Sheets: https://sheets.google.com")
    print("• Документация: https://developers.google.com/apps-script")

def main():
    """Основная функция - запуск всех тестов"""
    print("🔍 ПОШАГОВАЯ ДИАГНОСТИКА GOOGLE SHEETS")
    print("=" * 60)
    print("Этот скрипт проверит каждый компонент интеграции отдельно")
    print("для выявления точной причины проблемы.\n")
    
    tests = [
        ("Переменные окружения", step1_check_environment),
        ("Сетевое подключение", step2_test_network_connection),
        ("Простой POST запрос", step3_test_simple_post),
        ("Ping endpoint", step4_test_ping_endpoint),
        ("Запись данных", step5_test_data_write),
        ("Множественные запросы", step6_test_multiple_requests)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            
            if not result:
                print(f"\n⚠️  Тест '{test_name}' не прошел. Остановка диагностики.")
                break
                
        except Exception as e:
            print(f"\n❌ Критическая ошибка в тесте '{test_name}': {e}")
            results.append((test_name, False))
            break
    
    # Показываем сводку результатов
    print("\n" + "=" * 60)
    print("📊 СВОДКА РЕЗУЛЬТАТОВ ДИАГНОСТИКИ")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"• {test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Google Sheets интеграция работает корректно.")
    else:
        print(f"\n⚠️  ЕСТЬ ПРОБЛЕМЫ!")
        show_troubleshooting_guide()

if __name__ == "__main__":
    main()
