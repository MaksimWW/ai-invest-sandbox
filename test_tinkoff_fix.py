
#!/usr/bin/env python
"""
ТЕСТ: Исправление проблемы с проверкой Tinkoff API
"""

import os
from tinkoff_api import check_api_connection, get_prices_with_fallback

def test_tinkoff_fix():
    """Тестирует исправленную проверку подключения"""
    
    print("🔧 ТЕСТ: ИСПРАВЛЕНИЕ TINKOFF API")
    print("=" * 40)
    
    # Проверка токена
    token = os.getenv("TINKOFF_SANDBOX_TOKEN")
    print(f"🔑 Токен: {'✅ Настроен' if token else '❌ Отсутствует'}")
    
    if not token:
        print("⚠️ Токен не найден, тест завершен")
        return False
    
    print("\n📊 Тест 1: Получение цен")
    prices = get_prices_with_fallback()
    if prices:
        print("✅ Цены получены:")
        for ticker, price in prices.items():
            print(f"   • {ticker}: {price:.2f} ₽")
    else:
        print("❌ Ошибка получения цен")
        return False
    
    print("\n🔗 Тест 2: Проверка подключения API")
    if check_api_connection():
        print("✅ Подключение: УСПЕШНО")
    else:
        print("❌ Подключение: НЕУДАЧНО")
        return False
    
    print("\n🎉 Все тесты прошли успешно!")
    print("\n📱 Следующий шаг:")
    print("1. Отправьте команду /status в Telegram")
    print("2. Проверьте что теперь показывает ✅ для Tinkoff API")
    print("3. Отправьте команду /prices - должны быть реальные цены")
    
    return True

if __name__ == "__main__":
    test_tinkoff_fix()
