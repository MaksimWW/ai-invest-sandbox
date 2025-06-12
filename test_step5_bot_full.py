
#!/usr/bin/env python
"""
🔍 ШАГИ 5: Полное тестирование Telegram бота
==================================================
Запускаем все функции бота и проверяем их работу
"""

import os
import sys
import subprocess
import time
from dotenv import load_dotenv

def test_step5_bot_full():
    """Полное тестирование всех функций бота"""
    
    print("🔍 ШАГИ 5: Полное тестирование Telegram бота")
    print("=" * 60)
    
    load_dotenv()
    
    # Проверяем конфигурацию
    if not check_configuration():
        return False
    
    print("\n📋 ТЕСТИРУЕМЫЕ ФУНКЦИИ:")
    print("-" * 40)
    functions = [
        "1. Получение цен через Tinkoff API",
        "2. Генерация торговых сигналов SMA",
        "3. Подключение к Google Sheets",
        "4. Форматирование сообщений",
        "5. Автоматический режим (без Telegram)"
    ]
    
    for func in functions:
        print(f"  {func}")
    
    print(f"\n🔄 ЗАПУСК ТЕСТОВ:")
    print("-" * 30)
    
    # Тест 1: Получение цен
    if not test_tinkoff_prices():
        return False
    
    # Тест 2: Генерация сигналов
    if not test_trading_signals():
        return False
    
    # Тест 3: Google Sheets
    if not test_sheets_integration():
        return False
    
    # Тест 4: Форматирование сообщений
    if not test_message_formatting():
        return False
    
    # Тест 5: Автоматический режим
    if not test_automatic_mode():
        return False
    
    print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("-" * 40)
    
    show_next_steps()
    
    return True

def check_configuration():
    """Проверяет все необходимые настройки"""
    
    print("📋 1. ПРОВЕРКА КОНФИГУРАЦИИ")
    print("-" * 40)
    
    required_vars = [
        "TINKOFF_SANDBOX_TOKEN",
        "TELEGRAM_TOKEN", 
        "TELEGRAM_CHAT_ID",
        "SHEETS_WEBHOOK_URL",
        "SHEETS_TOKEN"
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "PLACEHOLDER":
            missing_vars.append(var)
            print(f"❌ {var}: НЕ НАСТРОЕН")
        else:
            masked = value[:5] + "..." if len(value) > 5 else "***"
            print(f"✅ {var}: {masked}")
    
    if missing_vars:
        print(f"\n⚠️  Не настроены переменные: {', '.join(missing_vars)}")
        print("🔧 Настройте их в .env файле перед продолжением")
        return False
    
    print("✅ Конфигурация в порядке!")
    return True

def test_tinkoff_prices():
    """Тестирует получение цен через Tinkoff API"""
    
    print(f"\n📋 2. ТЕСТ TINKOFF API")
    print("-" * 40)
    
    try:
        print("📤 Импортируем функции...")
        sys.path.append('.')
        from daily_plan_bot import get_last_prices
        
        print("📊 Получаем цены акций...")
        prices = get_last_prices()
        
        if not prices:
            print("❌ Цены не получены!")
            return False
        
        print("✅ Цены получены успешно:")
        for ticker, price in prices.items():
            print(f"   • {ticker}: {price:,.2f} ₽")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка получения цен: {e}")
        return False

def test_trading_signals():
    """Тестирует генерацию торговых сигналов"""
    
    print(f"\n📋 3. ТЕСТ ТОРГОВЫХ СИГНАЛОВ")
    print("-" * 40)
    
    try:
        print("📈 Импортируем функции...")
        from daily_plan_bot import get_signals
        
        print("🔍 Анализируем сигналы...")
        signals = get_signals()
        
        if not signals:
            print("❌ Сигналы не получены!")
            return False
        
        print("✅ Сигналы сгенерированы:")
        for ticker, signal in signals.items():
            emoji = "🟢" if signal == "BUY" else "🔴" if signal == "SELL" else "🟡"
            print(f"   • {ticker}: {signal} {emoji}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка генерации сигналов: {e}")
        return False

def test_sheets_integration():
    """Тестирует интеграцию с Google Sheets"""
    
    print(f"\n📋 4. ТЕСТ GOOGLE SHEETS")
    print("-" * 40)
    
    try:
        print("📝 Импортируем логгер...")
        from utils.sheets_logger import log_trade
        from datetime import datetime
        
        print("📤 Отправляем тестовую запись...")
        result = log_trade(
            date=datetime.now().date(),
            ticker="TEST_STEP5",
            figi="TEST_FIGI_STEP5",
            side="BUY",
            price=999.99,
            qty=1,
            fees=0.1
        )
        
        print(f"✅ Запись успешна: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка записи в Sheets: {e}")
        return False

def test_message_formatting():
    """Тестирует форматирование сообщений"""
    
    print(f"\n📋 5. ТЕСТ ФОРМАТИРОВАНИЯ")
    print("-" * 40)
    
    try:
        print("📝 Импортируем функции...")
        from daily_plan_bot import format_message
        
        # Тестовые данные
        test_prices = {"YNDX": 2510.35, "FXIT": 120.45}
        test_signals = {"YNDX": "BUY", "FXIT": "HOLD"}
        
        print("🔧 Форматируем сообщение...")
        message = format_message(test_prices, test_signals)
        
        print("✅ Сообщение сформировано:")
        print("=" * 30)
        print(message)
        print("=" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка форматирования: {e}")
        return False

def test_automatic_mode():
    """Тестирует автоматический режим"""
    
    print(f"\n📋 6. ТЕСТ АВТОМАТИЧЕСКОГО РЕЖИМА")
    print("-" * 40)
    
    try:
        print("🤖 Запускаем автоматический анализ...")
        from daily_plan_bot import run_daily_analysis
        
        # Запускаем анализ
        run_daily_analysis()
        
        print("✅ Автоматический режим работает!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка автоматического режима: {e}")
        return False

def show_next_steps():
    """Показывает следующие шаги"""
    
    print(f"\n🚀 СЛЕДУЮЩИЕ ШАГИ:")
    print("=" * 40)
    
    print("1️⃣ ТЕСТИРОВАНИЕ TELEGRAM КОМАНД:")
    print("   python daily_plan_bot.py bot")
    print("   Затем в Telegram отправьте:")
    print("   • /start")
    print("   • /prices") 
    print("   • /signals")
    print("   • /test_sheets")
    
    print("\n2️⃣ АВТОМАТИЧЕСКИЙ ЗАПУСК:")
    print("   python daily_plan_bot.py")
    print("   (анализ и отправка отчета)")
    
    print("\n3️⃣ НАСТРОЙКА АВТОЗАПУСКА:")
    print("   • Используйте cron для ежедневного запуска")
    print("   • Или настройте автозапуск в Replit")
    
    print(f"\n📚 ДОКУМЕНТАЦИЯ:")
    print("   • README.md - подробные инструкции")
    print("   • Google Sheets - журнал сделок")
    print("   • Telegram бот - интерактивные команды")

if __name__ == "__main__":
    success = test_step5_bot_full()
    
    if success:
        print(f"\n🎯 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
        print("Все компоненты работают корректно.")
    else:
        print(f"\n⚠️  ЕСТЬ ПРОБЛЕМЫ!")
        print("Исправьте ошибки и запустите тест снова.")
