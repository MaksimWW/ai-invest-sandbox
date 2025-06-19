
#!/usr/bin/env python
"""
🔍 ШАГ 1: ПРОВЕРКА ОКРУЖЕНИЯ И ЗАВИСИМОСТЕЙ
==================================================
"""

import os
import sys
from dotenv import load_dotenv

def test_step1_environment():
    """Проверяет базовое окружение и зависимости"""
    
    print("🔍 ШАГ 1: ПРОВЕРКА ОКРУЖЕНИЯ")
    print("=" * 50)
    
    # Загружаем переменные окружения
    load_dotenv()
    
    print("📦 1. ПРОВЕРКА ЗАВИСИМОСТЕЙ:")
    print("-" * 30)
    
    required_packages = [
        ("python-telegram-bot", "telegram"),
        ("requests", "requests"),
        ("python-dotenv", "dotenv"),
        ("tinkoff-investments", "tinkoff.invest"),
        ("openai", "openai"),
        ("pandas", "pandas"),
        ("numpy", "numpy")
    ]
    
    missing_packages = []
    
    for package_name, import_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name}")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n⚠️ Отсутствующие пакеты: {', '.join(missing_packages)}")
        return False
    
    print("\n🔧 2. ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ:")
    print("-" * 40)
    
    required_vars = [
        "TELEGRAM_TOKEN",
        "TELEGRAM_CHAT_ID", 
        "TINKOFF_SANDBOX_TOKEN",
        "OPENAI_API_KEY",
        "SHEETS_WEBHOOK_URL",
        "SHEETS_TOKEN"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "PLACEHOLDER":
            print(f"❌ {var}: не настроен")
            missing_vars.append(var)
        else:
            # Показываем только первые символы для безопасности
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"✅ {var}: {display_value}")
    
    if missing_vars:
        print(f"\n⚠️ Отсутствующие переменные: {', '.join(missing_vars)}")
        print("\n📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ:")
        for var in missing_vars:
            if var == "TELEGRAM_TOKEN":
                print("• TELEGRAM_TOKEN: получите у @BotFather в Telegram")
            elif var == "TELEGRAM_CHAT_ID":
                print("• TELEGRAM_CHAT_ID: напишите боту, затем https://api.telegram.org/bot<TOKEN>/getUpdates")
            elif var == "TINKOFF_SANDBOX_TOKEN":
                print("• TINKOFF_SANDBOX_TOKEN: получите в Tinkoff Invest API")
            elif var == "OPENAI_API_KEY":
                print("• OPENAI_API_KEY: получите на platform.openai.com")
            elif var == "SHEETS_WEBHOOK_URL":
                print("• SHEETS_WEBHOOK_URL: URL Google Apps Script")
            elif var == "SHEETS_TOKEN":
                print("• SHEETS_TOKEN: токен для авторизации с Google Sheets")
        return False
    
    print("\n📁 3. ПРОВЕРКА ФАЙЛОВ:")
    print("-" * 25)
    
    required_files = [
        "main.py",
        "daily_plan_bot_ptb.py",
        "requirements.txt",
        ".env"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            return False
    
    print("\n🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ!")
    print("🚀 Готов к переходу к Шагу 2")
    
    return True

if __name__ == "__main__":
    if test_step1_environment():
        print("\n➡️ СЛЕДУЮЩИЙ ШАГ:")
        print("python test_step2_telegram_basic.py")
    else:
        print("\n❌ Исправьте ошибки и запустите снова")
