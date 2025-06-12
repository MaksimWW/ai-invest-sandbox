
#!/usr/bin/env python
"""
🔍 ШАГИ 4: Тестирование Telegram бота
==================================================
Проверяем работу всех команд Telegram бота
"""

import os
import sys
from dotenv import load_dotenv

def test_step4_telegram_bot():
    """Тестирует команды Telegram бота"""
    
    print("🔍 ШАГИ 4: Тестирование Telegram бота")
    print("=" * 50)
    
    load_dotenv()
    
    # Проверяем наличие токенов
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not telegram_token or telegram_token == "PLACEHOLDER":
        print("❌ TELEGRAM_TOKEN не настроен!")
        print("📋 Для получения токена:")
        print("   1. Найдите @BotFather в Telegram")
        print("   2. Отправьте команду /newbot")
        print("   3. Следуйте инструкциям")
        print("   4. Добавьте токен в .env файл")
        return False
    
    if not telegram_chat_id:
        print("❌ TELEGRAM_CHAT_ID не настроен!")
        print("📋 Для получения Chat ID:")
        print("   1. Напишите боту любое сообщение")
        print("   2. Откройте: https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates")
        print("   3. Найдите 'chat':{'id':ЧИСЛО}")
        print("   4. Добавьте ID в .env файл")
        return False
    
    print(f"✅ TELEGRAM_TOKEN: {telegram_token[:10]}...")
    print(f"✅ TELEGRAM_CHAT_ID: {telegram_chat_id}")
    
    print("\n📋 ДОСТУПНЫЕ КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ:")
    print("-" * 40)
    
    commands = [
        ("/start", "Приветствие и список команд"),
        ("/test_sheets", "Проверка подключения к Google Sheets"),
        ("/log BUY YNDX 10 2500.50", "Запись тестовой сделки"),
        ("/prices", "Получение актуальных цен акций"),
        ("/signals", "Получение торговых сигналов"),
        ("/config", "Проверка конфигурации бота")
    ]
    
    for cmd, desc in commands:
        print(f"  {cmd:<25} - {desc}")
    
    print(f"\n🤖 ЗАПУСК TELEGRAM БОТА:")
    print("-" * 30)
    print("Для запуска бота выполните команду:")
    print("python daily_plan_bot.py bot")
    print("\nЗатем в Telegram отправьте команды боту для тестирования.")
    
    print(f"\n📊 АВТОМАТИЧЕСКИЙ РЕЖИМ (без Telegram):")
    print("-" * 40)
    print("Для тестирования автоматического анализа:")
    print("python daily_plan_bot.py")
    print("\nЭто протестирует:")
    print("• Получение цен через Tinkoff API")
    print("• Генерацию торговых сигналов")
    print("• Автоматическое логирование в Google Sheets")
    
    return True

def show_telegram_setup():
    """Показывает подробную инструкцию по настройке Telegram"""
    
    print("\n" + "=" * 60)
    print("📱 НАСТРОЙКА TELEGRAM БОТА")
    print("=" * 60)
    
    print("1️⃣ СОЗДАНИЕ БОТА:")
    print("   • Найдите @BotFather в Telegram")
    print("   • Отправьте команду /newbot")
    print("   • Придумайте имя для бота")
    print("   • Придумайте username (должен заканчиваться на 'bot')")
    print("   • Скопируйте полученный токен")
    
    print("\n2️⃣ ПОЛУЧЕНИЕ CHAT ID:")
    print("   • Напишите вашему боту любое сообщение")
    print("   • Откройте в браузере:")
    print("     https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates")
    print("   • Найдите: \"chat\":{\"id\":ЧИСЛО}")
    print("   • Скопируйте это число")
    
    print("\n3️⃣ ДОБАВЛЕНИЕ В .env:")
    print("   TELEGRAM_TOKEN=ваш_токен_от_botfather")
    print("   TELEGRAM_CHAT_ID=ваш_chat_id")

def check_bot_dependencies():
    """Проверяет установленные зависимости для бота"""
    
    print("\n📦 ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
    print("-" * 30)
    
    required_packages = [
        "telebot",
        "requests", 
        "python-dotenv",
        "tinkoff-investments"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Необходимо установить пакеты:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_step4_telegram_bot()
    
    if not success:
        show_telegram_setup()
    
    print("\n🔄 После настройки Telegram запустите:")
    print("python test_step4_telegram_bot.py")
    
    # Проверяем зависимости
    check_bot_dependencies()
