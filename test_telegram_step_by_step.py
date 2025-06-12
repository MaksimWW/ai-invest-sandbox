
#!/usr/bin/env python
"""
🤖 ПОШАГОВОЕ ТЕСТИРОВАНИЕ TELEGRAM БОТА
==================================================
Тестируем каждую команду бота отдельно с детальными инструкциями
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv

def step1_check_telegram_config():
    """ШАГ 1: Проверка конфигурации Telegram"""
    
    print("🔍 ШАГ 1: ПРОВЕРКА КОНФИГУРАЦИИ TELEGRAM")
    print("=" * 60)
    
    load_dotenv()
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("📋 Проверяем переменные окружения:")
    
    if not telegram_token or telegram_token == "PLACEHOLDER":
        print("❌ TELEGRAM_TOKEN не настроен!")
        print("\n🔧 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:")
        print("1. Найдите @BotFather в Telegram")
        print("2. Отправьте команду /newbot")
        print("3. Следуйте инструкциям для создания бота")
        print("4. Скопируйте полученный токен")
        print("5. Добавьте в файл .env:")
        print("   TELEGRAM_TOKEN=ваш_токен_от_botfather")
        return False
    
    if not telegram_chat_id or telegram_chat_id == "PLACEHOLDER":
        print("❌ TELEGRAM_CHAT_ID не настроен!")
        print("\n🔧 ИНСТРУКЦИЯ ПО ПОЛУЧЕНИЮ CHAT_ID:")
        print("1. Напишите вашему боту любое сообщение")
        print("2. Откройте в браузере:")
        print(f"   https://api.telegram.org/bot{telegram_token}/getUpdates")
        print("3. Найдите 'chat':{'id':ЧИСЛО}")
        print("4. Добавьте в файл .env:")
        print("   TELEGRAM_CHAT_ID=найденное_число")
        return False
    
    print(f"✅ TELEGRAM_TOKEN: {telegram_token[:10]}...")
    print(f"✅ TELEGRAM_CHAT_ID: {telegram_chat_id}")
    
    return True

def step2_test_bot_connection():
    """ШАГ 2: Тест подключения к Telegram API"""
    
    print("\n🔍 ШАГ 2: ТЕСТ ПОДКЛЮЧЕНИЯ К TELEGRAM API")
    print("=" * 60)
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    
    print("📡 Проверяем доступность Telegram API...")
    
    try:
        # Проверяем информацию о боте
        url = f"https://api.telegram.org/bot{telegram_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                bot_data = bot_info["result"]
                print(f"✅ Бот найден: @{bot_data['username']}")
                print(f"📋 Имя бота: {bot_data['first_name']}")
                print(f"🆔 ID бота: {bot_data['id']}")
                return True
            else:
                print("❌ Ошибка в ответе API")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def step3_send_test_message():
    """ШАГ 3: Отправка тестового сообщения"""
    
    print("\n🔍 ШАГ 3: ОТПРАВКА ТЕСТОВОГО СООБЩЕНИЯ")
    print("=" * 60)
    
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print("📤 Отправляем тестовое сообщение боту...")
    
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        payload = {
            "chat_id": telegram_chat_id,
            "text": "🧪 Тестовое сообщение от бота\n\nЕсли вы видите это сообщение, значит бот работает правильно!"
        }
        
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Тестовое сообщение отправлено успешно!")
                print("📱 Проверьте Telegram - должно прийти сообщение")
                return True
            else:
                print(f"❌ Ошибка отправки: {result}")
                return False
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

def step4_instructions_for_bot_start():
    """ШАГ 4: Инструкции по запуску бота"""
    
    print("\n🔍 ШАГ 4: ЗАПУСК TELEGRAM БОТА")
    print("=" * 60)
    
    print("🚀 ИНСТРУКЦИЯ ПО ЗАПУСКУ:")
    print("1. Откройте новый терминал в Replit")
    print("2. Выполните команду:")
    print("   python daily_plan_bot.py bot")
    print("3. Дождитесь сообщения '🤖 Telegram бот запущен...'")
    print("4. НЕ ЗАКРЫВАЙТЕ терминал - бот должен работать постоянно")
    
    print("\n⚠️  ВАЖНО:")
    print("• Бот должен работать в фоне для обработки команд")
    print("• Если закроете терминал, бот перестанет отвечать")
    print("• Для остановки бота нажмите Ctrl+C в терминале")
    
    return True

def step5_test_commands_list():
    """ШАГ 5: Список команд для тестирования"""
    
    print("\n🔍 ШАГ 5: КОМАНДЫ ДЛЯ ТЕСТИРОВАНИЯ")
    print("=" * 60)
    
    print("📋 ТЕСТИРУЙТЕ КОМАНДЫ В СЛЕДУЮЩЕМ ПОРЯДКЕ:")
    print("(отправляйте команды боту в Telegram)")
    
    commands = [
        ("1️⃣", "/help", "Получить список всех команд", "Должен показать справку"),
        ("2️⃣", "/config", "Проверить конфигурацию Google Sheets", "Показать статус настроек"),
        ("3️⃣", "/test_sheets", "Протестировать подключение к Sheets", "Записать тестовую запись"),
        ("4️⃣", "/prices", "Получить актуальные цены акций", "Показать цены YNDX и FXIT"),
        ("5️⃣", "/signals", "Получить торговые сигналы", "Показать сигналы BUY/SELL/HOLD"),
        ("6️⃣", "/log BUY YNDX 10 2500.50", "Записать тестовую сделку", "Записать сделку в Sheets"),
        ("7️⃣", "/debug", "Показать последние логи", "Показать отладочную информацию")
    ]
    
    for num, cmd, desc, expected in commands:
        print(f"\n{num} КОМАНДА: {cmd}")
        print(f"   📝 Описание: {desc}")
        print(f"   ✅ Ожидаемый результат: {expected}")
    
    print("\n🔄 ПОРЯДОК ТЕСТИРОВАНИЯ:")
    print("1. Запустите бота: python daily_plan_bot.py bot")
    print("2. Откройте Telegram и найдите вашего бота")
    print("3. Отправляйте команды по очереди")
    print("4. Проверяйте ответы бота")
    print("5. Если команда не работает - проверьте логи в терминале")
    
    return True

def step6_troubleshooting():
    """ШАГ 6: Решение проблем"""
    
    print("\n🔍 ШАГ 6: РЕШЕНИЕ ПРОБЛЕМ")
    print("=" * 60)
    
    print("🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ И РЕШЕНИЯ:")
    
    problems = [
        ("Бот не отвечает на команды", [
            "• Проверьте, что бот запущен (python daily_plan_bot.py bot)",
            "• Убедитесь, что терминал с ботом не закрыт",
            "• Проверьте TELEGRAM_TOKEN и TELEGRAM_CHAT_ID в .env"
        ]),
        ("Команда /test_sheets не работает", [
            "• Проверьте SHEETS_WEBHOOK_URL в .env",
            "• Убедитесь, что Google Apps Script опубликован",
            "• Проверьте SHEETS_TOKEN в .env и скрипте"
        ]),
        ("Команда /prices не работает", [
            "• Проверьте TINKOFF_SANDBOX_TOKEN в .env",
            "• Убедитесь, что токен активен",
            "• Проверьте подключение к интернету"
        ]),
        ("Команда /log не записывает данные", [
            "• Проверьте формат: /log BUY TICKER QTY PRICE",
            "• Используйте только YNDX или FXIT как тикеры",
            "• Убедитесь, что Google Sheets доступны"
        ])
    ]
    
    for problem, solutions in problems:
        print(f"\n❌ {problem}:")
        for solution in solutions:
            print(f"   {solution}")
    
    print("\n🔧 ДОПОЛНИТЕЛЬНАЯ ОТЛАДКА:")
    print("• Смотрите логи в терминале где запущен бот")
    print("• Используйте команду /debug для просмотра логов")
    print("• Проверьте файл debug_sheets.log для ошибок Sheets")
    
    return True

def main():
    """Основная функция - запускает все шаги"""
    
    print("🤖 ПОШАГОВОЕ ТЕСТИРОВАНИЕ TELEGRAM БОТА")
    print("=" * 70)
    print("Этот скрипт проведет вас через все этапы тестирования")
    print("=" * 70)
    
    # Шаг 1: Проверка конфигурации
    if not step1_check_telegram_config():
        print("\n❌ Конфигурация не пройдена. Исправьте ошибки и запустите снова.")
        return
    
    # Шаг 2: Тест подключения
    if not step2_test_bot_connection():
        print("\n❌ Подключение к Telegram API не работает.")
        return
    
    # Шаг 3: Тест отправки сообщения
    if not step3_send_test_message():
        print("\n❌ Отправка сообщений не работает.")
        return
    
    # Шаг 4: Инструкции по запуску
    step4_instructions_for_bot_start()
    
    # Шаг 5: Список команд
    step5_test_commands_list()
    
    # Шаг 6: Решение проблем
    step6_troubleshooting()
    
    print("\n" + "=" * 70)
    print("🎉 ПОДГОТОВКА К ТЕСТИРОВАНИЮ ЗАВЕРШЕНА!")
    print("=" * 70)
    print("📋 СЛЕДУЮЩИЕ ШАГИ:")
    print("1. Запустите бота: python daily_plan_bot.py bot")
    print("2. Тестируйте команды в Telegram по списку выше")
    print("3. Сообщайте о любых проблемах для решения")

if __name__ == "__main__":
    main()
