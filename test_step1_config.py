
#!/usr/bin/env python
import os
from dotenv import load_dotenv

def test_step1_config():
    """Шаг 1: Проверка базовой конфигурации и переменных окружения"""
    
    print("🔍 ШАГИ 1: Проверка конфигурации")
    print("=" * 50)
    
    # Загружаем .env файл
    load_dotenv()
    
    # Список всех необходимых переменных
    required_vars = {
        "TINKOFF_SANDBOX_TOKEN": "Токен Tinkoff API",
        "TELEGRAM_TOKEN": "Токен Telegram бота", 
        "TELEGRAM_CHAT_ID": "ID чата Telegram",
        "SHEETS_WEBHOOK_URL": "URL webhook Google Sheets",
        "SHEETS_TOKEN": "Токен для Google Sheets"
    }
    
    print("📋 Проверяем переменные окружения:")
    print("-" * 30)
    
    all_ok = True
    
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        
        if value:
            # Показываем только первые и последние символы для безопасности
            if len(value) > 10:
                masked_value = value[:5] + "..." + value[-5:]
            else:
                masked_value = value[:3] + "..."
            
            print(f"✅ {var_name}: {masked_value}")
        else:
            print(f"❌ {var_name}: НЕ НАЙДЕНО")
            all_ok = False
        
        print(f"   ({description})")
        print()
    
    # Проверяем .env файл
    print("📁 Проверяем .env файл:")
    print("-" * 30)
    
    if os.path.exists(".env"):
        print("✅ Файл .env существует")
        
        # Читаем размер файла
        file_size = os.path.getsize(".env")
        print(f"📊 Размер файла: {file_size} байт")
        
        # Проверяем содержимое (без вывода секретов)
        with open(".env", "r") as f:
            lines = f.readlines()
            non_empty_lines = [line for line in lines if line.strip() and not line.startswith("#")]
            print(f"📝 Количество настроек: {len(non_empty_lines)}")
    else:
        print("❌ Файл .env НЕ НАЙДЕН!")
        all_ok = False
    
    print("\n" + "=" * 50)
    
    if all_ok:
        print("✅ ВСЕ ПЕРЕМЕННЫЕ НАСТРОЕНЫ КОРРЕКТНО!")
        print("🚀 Можно переходить к следующему шагу")
        return True
    else:
        print("❌ НАЙДЕНЫ ПРОБЛЕМЫ В КОНФИГУРАЦИИ!")
        print("🔧 Необходимо исправить перед продолжением")
        return False

if __name__ == "__main__":
    test_step1_config()
