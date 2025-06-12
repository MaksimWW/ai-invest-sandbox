
#!/usr/bin/env python
import os
import requests

def test_webhook_simple():
    """Простая проверка webhook без записи в таблицу"""
    
    webhook_url = os.getenv("SHEETS_WEBHOOK_URL")
    token = os.getenv("SHEETS_TOKEN")
    
    if not webhook_url or not token:
        print("❌ Переменные SHEETS_WEBHOOK_URL или SHEETS_TOKEN не найдены в .env")
        return False
    
    print(f"🔗 Тестируем webhook: {webhook_url}")
    print(f"🔑 Токен: {token}")
    
    # Простой тест - отправляем только токен
    payload = {
        "token": token,
        "test": "ping"
    }
    
    try:
        print("📤 Отправляем тестовый запрос...")
        response = requests.post(webhook_url, data=payload, timeout=10)
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📝 Тело ответа: {response.text[:500]}...")
        
        if response.status_code == 200:
            print("✅ Webhook доступен!")
            
            # Проверяем, что это не HTML страница с ошибкой
            if response.text.startswith('<!DOCTYPE html>') or '<html>' in response.text:
                print("⚠️  Получен HTML ответ - возможно ошибка в скрипте")
                return False
            else:
                print("✅ Получен корректный ответ от скрипта")
                return True
        else:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут запроса - webhook недоступен")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сетевого запроса: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Простой тест подключения к Google Apps Script webhook")
    print("=" * 50)
    test_webhook_simple()
