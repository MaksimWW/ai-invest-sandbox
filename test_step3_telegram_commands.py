
#!/usr/bin/env python
"""
🔍 ШАГ 3: ТЕСТИРОВАНИЕ КОМАНД TELEGRAM БОТА
==================================================
Проверяем расширенный функционал бота - дополнительные команды
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

def test_step3_telegram_commands():
    """Тестирует команды Telegram бота"""
    
    print("🔍 ШАГ 3: ТЕСТИРОВАНИЕ КОМАНД TELEGRAM БОТА")
    print("=" * 60)
    
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("📋 1. ДОБАВЛЕНИЕ КОМАНД В БОТА:")
    print("-" * 40)
    
    # Проверяем, есть ли в боте дополнительные команды
    print("⚠️  ВНИМАНИЕ: Сейчас бот поддерживает только /start")
    print("Нужно добавить дополнительные команды для полного тестирования.")
    print("")
    
    print("📝 КОМАНДЫ ДЛЯ ДОБАВЛЕНИЯ:")
    print("• /prices - показать цены акций")
    print("• /signals - показать торговые сигналы") 
    print("• /help - показать справку")
    print("• /status - показать статус системы")
    
    print(f"\n📋 2. ИНСТРУКЦИИ ДЛЯ РУЧНОГО ТЕСТИРОВАНИЯ:")
    print("-" * 50)
    print("После добавления команд протестируйте их в Telegram:")
    print("")
    print("📱 КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ:")
    print("   /start - базовое приветствие")
    print("   /help - список команд")
    print("   /prices - текущие цены")
    print("   /signals - торговые сигналы")
    print("   /status - статус системы")
    print("")
    print("✅ КРИТЕРИИ УСПЕХА:")
    print("   • Все команды отвечают")
    print("   • Нет ошибок в консоли")
    print("   • Сообщения корректно форматированы")
    
    return True

def send_test_command(command):
    """Отправляет тестовую команду боту"""
    
    load_dotenv()
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        
        payload = {
            "chat_id": telegram_chat_id,
            "text": command,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print(f"✅ Команда '{command}' отправлена")
                return True
        
        print(f"❌ Ошибка отправки команды '{command}'")
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def check_bot_improvements_needed():
    """Проверяет, нужны ли улучшения в боте"""
    
    print(f"\n📋 3. АНАЛИЗ ТЕКУЩЕГО БОТА:")
    print("-" * 40)
    
    # Проверяем файл daily_plan_bot_ptb.py
    try:
        with open("daily_plan_bot_ptb.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        commands_found = []
        if "cmd_start" in content:
            commands_found.append("/start")
        if "cmd_help" in content:
            commands_found.append("/help")
        if "cmd_prices" in content:
            commands_found.append("/prices")
        if "cmd_signals" in content:
            commands_found.append("/signals")
        if "cmd_status" in content:
            commands_found.append("/status")
            
        print(f"🔍 Найденные команды: {', '.join(commands_found) if commands_found else 'Только /start'}")
        
        if len(commands_found) <= 1:
            print("⚠️  НУЖНО ДОБАВИТЬ КОМАНДЫ!")
            return True
        else:
            print("✅ Команды уже добавлены")
            return False
            
    except FileNotFoundError:
        print("❌ Файл daily_plan_bot_ptb.py не найден")
        return True
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return True

if __name__ == "__main__":
    print("🤖 ТЕСТИРОВАНИЕ КОМАНД TELEGRAM БОТА")
    print("=" * 60)
    
    needs_improvement = check_bot_improvements_needed()
    
    if needs_improvement:
        print(f"\n⚠️  ТРЕБУЕТСЯ ДОРАБОТКА БОТА")
        print("-" * 30)
        print("Сначала нужно добавить команды в daily_plan_bot_ptb.py")
        print("Затем запустить этот тест снова.")
    else:
        success = test_step3_telegram_commands()
        
        if success:
            print(f"\n🎉 ШАГ 3: ГОТОВ К ТЕСТИРОВАНИЮ!")
            print("-" * 40)
            print("➡️ СЛЕДУЮЩИЕ ДЕЙСТВИЯ:")
            print("1. Убедитесь, что бот запущен")
            print("2. Протестируйте все команды в Telegram")
            print("3. Если всё работает → запустите: python test_step4_telegram_bot.py")
