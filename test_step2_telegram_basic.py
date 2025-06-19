
#!/usr/bin/env python
"""
🔍 ШАГ 2: ТЕСТИРОВАНИЕ БАЗОВОГО TELEGRAM БОТА
==================================================
Проверяем, что бот может подключиться к Telegram API и отвечать на команды
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

def test_step2_telegram_basic():
    """Тестирует базовое подключение к Telegram API"""
    
    print("🔍 ШАГ 2: ТЕСТИРОВАНИЕ БАЗОВОГО TELEGRAM БОТА")
    print("=" * 60)
    
    load_dotenv()
    
    # Получаем переменные
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("📋 1. ПРОВЕРКА API СОЕДИНЕНИЯ:")
    print("-" * 40)
    
    # Тест 1: Проверка токена через getMe
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_name = bot_info["result"]["first_name"]
                bot_username = bot_info["result"]["username"]
                print(f"✅ Бот подключен: {bot_name} (@{bot_username})")
            else:
                print("❌ API вернул ошибку:", bot_info)
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к Telegram API: {e}")
        return False
    
    print("\n📋 2. ПРОВЕРКА ОТПРАВКИ СООБЩЕНИЙ:")
    print("-" * 40)
    
    # Тест 2: Отправка тестового сообщения
    try:
        test_message = "🧪 ТЕСТ ШАГ 2: Проверка отправки сообщений"
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        
        payload = {
            "chat_id": telegram_chat_id,
            "text": test_message,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                message_id = result["result"]["message_id"]
                print(f"✅ Тестовое сообщение отправлено (ID: {message_id})")
            else:
                print("❌ Ошибка отправки:", result)
                return False
        else:
            print(f"❌ HTTP ошибка при отправке: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отправки сообщения: {e}")
        return False
    
    print(f"\n📋 3. ИНСТРУКЦИИ ДЛЯ РУЧНОГО ТЕСТИРОВАНИЯ:")
    print("-" * 50)
    print("Теперь нужно запустить бота и протестировать команды вручную.")
    print("")
    print("🚀 ЗАПУСК БОТА:")
    print("   python daily_plan_bot_ptb.py")
    print("")
    print("📱 КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ В TELEGRAM:")
    print("   /start - должен ответить приветствием")
    print("")
    print("⏰ ВРЕМЯ НА ТЕСТИРОВАНИЕ: 2-3 минуты")
    print("")
    print("✅ КРИТЕРИИ УСПЕХА:")
    print("   • Бот запустился без ошибок")
    print("   • Команда /start работает")
    print("   • Бот отвечает на сообщения")
    
    return True

def check_bot_running():
    """Проверяет, запущен ли бот"""
    
    print(f"\n📋 4. ПРОВЕРКА ЗАПУЩЕННОГО БОТА:")
    print("-" * 40)
    
    # Простая проверка через ps
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'daily_plan_bot_ptb.py' in result.stdout:
            print("✅ Процесс бота найден в системе")
            return True
        else:
            print("⚠️  Процесс бота не найден")
            print("   Возможно, бот не запущен или завершился")
            return False
    except Exception as e:
        print(f"⚠️  Не удалось проверить процессы: {e}")
        return False

if __name__ == "__main__":
    print("🤖 АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ TELEGRAM БОТА")
    print("=" * 60)
    
    success = test_step2_telegram_basic()
    
    if success:
        print(f"\n🎉 ШАГ 2: БАЗОВЫЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
        print("-" * 40)
        print("➡️ СЛЕДУЮЩИЕ ДЕЙСТВИЯ:")
        print("1. Запустите бота: python daily_plan_bot_ptb.py")
        print("2. Отправьте команду /start в Telegram")
        print("3. Если всё работает → запустите: python test_step3_telegram_commands.py")
    else:
        print(f"\n❌ ШАГ 2: ЕСТЬ ПРОБЛЕМЫ!")
        print("-" * 30)
        print("Исправьте ошибки выше и повторите тест.")
