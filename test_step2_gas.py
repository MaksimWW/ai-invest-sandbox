
#!/usr/bin/env python
"""
🔍 ШАГИ 2: Тестирование Google Apps Script
==================================================
Проверяем работу Google Apps Script webhook
"""

import os
import requests
import json
from datetime import datetime

def test_google_apps_script():
    """Тестирует работу Google Apps Script webhook"""
    
    print("🔍 ШАГИ 2: Тестирование Google Apps Script")
    print("=" * 50)
    
    # Получаем конфигурацию
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    if not webhook_url or not token:
        print("❌ ОШИБКА: SHEETS_WEBHOOK_URL или SHEETS_TOKEN не настроены!")
        return False
    
    print("📡 Отправляем тестовый запрос...")
    print(f"🔗 URL: {webhook_url[:50]}...")
    print(f"🔑 Token: {token[:10]}...")
    
    # Тестовые данные
    test_payload = {
        "date": "2025-06-12",
        "ticker": "TEST",
        "figi": "TEST_FIGI", 
        "side": "BUY",
        "price": 100.0,
        "qty": 1,
        "fees": 0.1,
        "token": token
    }
    
    try:
        print("\n📤 Отправляем данные...")
        print(f"📋 Payload: {json.dumps(test_payload, ensure_ascii=False)}")
        
        response = requests.post(
            webhook_url,
            json=test_payload,
            timeout=30,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'TinkoffBot/1.0'
            }
        )
        
        print(f"\n📥 Получен ответ:")
        print(f"🔢 HTTP Status: {response.status_code}")
        print(f"📋 Headers: {dict(response.headers)}")
        
        response_text = response.text.strip()
        print(f"📄 Body: {response_text[:500]}...")
        
        # Анализируем ответ
        if response.status_code == 200:
            if response_text == "OK":
                print("\n✅ ТЕСТ УСПЕШЕН!")
                print("✅ Google Apps Script работает корректно")
                print("✅ Данные записаны в таблицу")
                return True
            elif response_text.startswith('<!DOCTYPE html>') or '<html>' in response_text:
                print("\n❌ ОШИБКА: Получен HTML вместо ответа!")
                
                # Извлекаем ошибку из HTML
                error_msg = "Неизвестная ошибка"
                if 'TypeError:' in response_text:
                    start = response_text.find('TypeError:')
                    end = response_text.find('</div>', start)
                    if end == -1:
                        end = response_text.find('(line', start)
                    if end != -1:
                        error_msg = response_text[start:end].strip()
                
                print(f"🔍 Ошибка: {error_msg}")
                print("\n🔧 ВОЗМОЖНЫЕ ПРИЧИНЫ:")
                print("1. Неправильный ID таблицы Google Sheets")
                print("2. Скрипт не имеет доступа к таблице")
                print("3. Неправильное имя листа (должно быть 'Sheet1' или 'Лист1')")
                print("4. Скрипт не опубликован как веб-приложение")
                
                return False
            else:
                print(f"\n⚠️ НЕОЖИДАННЫЙ ОТВЕТ: {response_text}")
                return False
        else:
            print(f"\n❌ ОШИБКА HTTP: {response.status_code}")
            print(f"📄 Ответ: {response_text}")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ ОШИБКА: Таймаут запроса (30 сек)")
        print("🔧 Проверьте доступность URL")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n❌ ОШИБКА СЕТИ: {e}")
        return False
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return False

def check_gas_requirements():
    """Проверяет требования для Google Apps Script"""
    
    print("\n📋 Проверка требований для Google Apps Script:")
    print("-" * 40)
    
    requirements = [
        "1. Создана Google Sheets таблица",
        "2. Создан Google Apps Script проект", 
        "3. Скрипт имеет код из файла new_google_apps_script.js",
        "4. Скрипт опубликован как веб-приложение",
        "5. URL веб-приложения добавлен в SHEETS_WEBHOOK_URL",
        "6. Секретный токен добавлен в SHEETS_TOKEN"
    ]
    
    for req in requirements:
        print(f"📝 {req}")
    
    print("\n💡 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:")
    print("1. Откройте https://script.google.com")
    print("2. Создайте новый проект")
    print("3. Замените код на содержимое new_google_apps_script.js")
    print("4. Измените SHEET_ID на ID вашей таблицы")
    print("5. Нажмите 'Развернуть' -> 'Новое развертывание'")
    print("6. Выберите тип 'Веб-приложение'")
    print("7. Скопируйте URL и добавьте в переменные окружения")

if __name__ == "__main__":
    success = test_google_apps_script()
    
    if not success:
        check_gas_requirements()
        print("\n🔄 После исправления запустите тест снова:")
        print("python test_step2_gas.py")
    else:
        print("\n🚀 Готово! Можно переходить к следующему шагу")
