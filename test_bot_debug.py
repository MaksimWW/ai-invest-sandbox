
#!/usr/bin/env python
"""
🔍 ОТЛАДКА TELEGRAM БОТА
==================================================
Проверяем подключение и отправляем тестовое сообщение
"""

import os
import asyncio
import requests
from dotenv import load_dotenv

async def test_bot_connection():
    """Тестирует подключение к боту"""
    
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("🔍 ТЕСТИРОВАНИЕ ПОДКЛЮЧЕНИЯ К БОТУ")
    print("=" * 50)
    
    if not token:
        print("❌ TELEGRAM_TOKEN не найден!")
        return False
        
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID не найден!")
        return False
    
    print(f"✅ Token: {token[:15]}...")
    print(f"✅ Chat ID: {chat_id}")
    
    # Проверяем бота
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                bot_info = result["result"]
                print(f"✅ Бот найден: {bot_info['first_name']} (@{bot_info.get('username', 'unknown')})")
            else:
                print(f"❌ Ошибка API: {result}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False
    
    # Отправляем тестовое сообщение
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": "🧪 ТЕСТ ОТЛАДКИ: Бот получает сообщения?",
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ Тестовое сообщение отправлено (ID: {result['result']['message_id']})")
                return True
        
        print(f"❌ Ошибка отправки: {response.text}")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_bot_connection())
    
    if success:
        print(f"\n🎉 ТЕСТ ПРОЙДЕН!")
        print("-" * 30)
        print("✅ Бот может отправлять сообщения")
        print("✅ Проверьте Telegram - должно прийти тестовое сообщение")
        print("\n📋 СЛЕДУЮЩИЕ ДЕЙСТВИЯ:")
        print("1. Перезапустите бота с отладкой: python daily_plan_bot_ptb.py")
        print("2. Отправьте команду /start")
        print("3. Смотрите логи в консоли")
    else:
        print(f"\n❌ ТЕСТ НЕ ПРОЙДЕН!")
        print("-" * 30)
        print("Проверьте настройки TELEGRAM_TOKEN и TELEGRAM_CHAT_ID")
