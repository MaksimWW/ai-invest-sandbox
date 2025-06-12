
#!/usr/bin/env python
"""
🔍 ШАГИ 3: Детальная диагностика Google Apps Script
==================================================
Проверяем каждый аспект настройки Google Apps Script
"""

import os
import requests
import json
from dotenv import load_dotenv

def test_step3_gas_debug():
    """Детальная диагностика Google Apps Script"""
    
    print("🔍 ШАГИ 3: Детальная диагностика Google Apps Script")
    print("=" * 60)
    
    load_dotenv()
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    print("📋 1. ПРОВЕРКА КОНФИГУРАЦИИ")
    print("-" * 40)
    
    if not webhook_url:
        print("❌ SHEETS_WEBHOOK_URL не найден в .env")
        return False
    
    if not token:
        print("❌ SHEETS_TOKEN не найден в .env") 
        return False
    
    print(f"✅ URL: {webhook_url[:50]}...")
    print(f"✅ Token: {token}")
    
    # Проверяем формат URL
    if not webhook_url.startswith("https://script.google.com/macros/s/"):
        print("⚠️  URL не похож на Google Apps Script webhook")
        print("   Правильный формат: https://script.google.com/macros/s/SCRIPT_ID/exec")
    
    print("\n📋 2. ТЕСТ PING (без записи в таблицу)")
    print("-" * 40)
    
    # Тест 1: Простой ping
    ping_payload = {
        "test": "ping",
        "token": token
    }
    
    try:
        print("📤 Отправляем ping запрос...")
        response = requests.post(webhook_url, data=ping_payload, timeout=15)
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📄 Response: {response.text[:200]}...")
        
        if response.status_code != 200:
            print(f"❌ Неожиданный HTTP статус: {response.status_code}")
            return False
            
        # Проверяем тип ответа
        if response.text.startswith('<!DOCTYPE html>') or '<html>' in response.text:
            print("❌ Получен HTML вместо JSON - скрипт не работает")
            analyze_html_error(response.text)
            return False
            
        # Пытаемся распарсить JSON
        try:
            json_response = json.loads(response.text)
            print(f"✅ Получен JSON ответ: {json_response}")
            
            if json_response.get("ok") == True:
                print("✅ Ping тест успешен!")
            elif json_response.get("error") == "Unauthorized":
                print("❌ Ошибка авторизации - неправильный токен")
                print(f"   Ожидаемый токен в скрипте: {token}")
                print("   Проверьте, что токен в скрипте совпадает с .env")
                return False
            else:
                print(f"⚠️  Неожиданный ответ: {json_response}")
                
        except json.JSONDecodeError:
            print(f"⚠️  Ответ не является JSON: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса - скрипт не отвечает")
        return False
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
        return False
    
    print("\n📋 3. ТЕСТ ЗАПИСИ В ТАБЛИЦУ")
    print("-" * 40)
    
    # Тест 2: Запись данных
    test_payload = {
        "date": "2025-06-12",
        "ticker": "TEST",
        "figi": "TEST_FIGI",
        "side": "BUY", 
        "price": "100.0",
        "qty": "1",
        "fees": "0.1",
        "token": token
    }
    
    try:
        print("📤 Отправляем данные для записи...")
        response = requests.post(webhook_url, data=test_payload, timeout=15)
        
        print(f"📊 HTTP Status: {response.status_code}")
        print(f"📄 Response: {response.text[:300]}...")
        
        if response.text.startswith('<!DOCTYPE html>'):
            print("❌ Получен HTML - ошибка в скрипте при записи")
            analyze_html_error(response.text)
            return False
            
        try:
            json_response = json.loads(response.text)
            
            if json_response.get("ok") == True:
                print("✅ Запись в таблицу успешна!")
                print(f"✅ Данные: {json_response.get('data', 'N/A')}")
                return True
            else:
                print(f"❌ Ошибка записи: {json_response.get('error', 'Unknown')}")
                return False
                
        except json.JSONDecodeError:
            if response.text.strip() == "OK":
                print("✅ Получен ответ 'OK' - запись успешна!")
                return True
            else:
                print(f"⚠️  Неизвестный формат ответа: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Ошибка при записи: {e}")
        return False

def analyze_html_error(html_text):
    """Анализирует HTML ошибку от Google Apps Script"""
    
    print("\n🔍 АНАЛИЗ HTML ОШИБКИ:")
    print("-" * 30)
    
    # Ищем типичные ошибки
    error_patterns = {
        "TypeError": "Ошибка типа данных",
        "ReferenceError": "Переменная не найдена", 
        "openById": "Проблема с ID таблицы",
        "appendRow": "Проблема с записью в лист",
        "getActiveSheet": "Проблема с доступом к листу",
        "Authorization": "Проблема с правами доступа"
    }
    
    found_errors = []
    
    for pattern, description in error_patterns.items():
        if pattern in html_text:
            found_errors.append(f"• {description} (найдено: {pattern})")
    
    if found_errors:
        print("🚨 Найденные проблемы:")
        for error in found_errors:
            print(f"   {error}")
    else:
        print("❓ Конкретная ошибка не определена")
    
    # Специальные советы
    if "openById" in html_text:
        print("\n💡 РЕШЕНИЕ:")
        print("1. Проверьте ID таблицы в Google Apps Script")
        print("2. Убедитесь, что таблица существует и доступна")
        print("3. ID берется из URL: docs.google.com/spreadsheets/d/ID_ЗДЕСЬ/edit")
        
    elif "appendRow" in html_text:
        print("\n💡 РЕШЕНИЕ:")
        print("1. Проверьте имя листа (Sheet1, Лист1)")
        print("2. Убедитесь, что у скрипта есть права на запись")
        print("3. Попробуйте пересоздать лист")

def show_gas_checklist():
    """Показывает чеклист для настройки Google Apps Script"""
    
    print("\n" + "=" * 60)
    print("📋 ЧЕКЛИСТ НАСТРОЙКИ GOOGLE APPS SCRIPT")
    print("=" * 60)
    
    checklist = [
        "□ Создана Google Sheets таблица",
        "□ Скопирован ID таблицы из URL",
        "□ Создан проект в script.google.com",
        "□ Вставлен код из new_google_apps_script.js",
        "□ В коде заменен SPREADSHEET_ID на реальный ID",
        "□ В коде проверен токен (должен быть 'mySecret123')",
        "□ Скрипт сохранен (Ctrl+S)",
        "□ Нажато 'Развернуть' -> 'Новое развертывание'",
        "□ Выбран тип 'Веб-приложение'",
        "□ Доступ 'Все пользователи'",
        "□ Скопирован URL веб-приложения",
        "□ URL добавлен в SHEETS_WEBHOOK_URL в .env"
    ]
    
    for item in checklist:
        print(f"  {item}")
    
    print(f"\n🔧 ТЕКУЩАЯ КОНФИГУРАЦИЯ:")
    print(f"   Token в .env: {os.getenv('SHEETS_TOKEN', 'НЕ НАЙДЕН')}")
    print(f"   URL в .env: {os.getenv('SHEETS_WEBHOOK_URL', 'НЕ НАЙДЕН')[:50]}...")

if __name__ == "__main__":
    success = test_step3_gas_debug()
    
    if not success:
        show_gas_checklist()
        print("\n🔄 После исправления запустите:")
        print("python test_step3_gas_debug.py")
    else:
        print("\n🎉 Google Apps Script работает корректно!")
        print("🚀 Можно переходить к следующему шагу тестирования")
