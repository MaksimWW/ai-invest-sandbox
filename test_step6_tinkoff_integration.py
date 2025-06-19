
#!/usr/bin/env python
"""
ТЕСТ ШАГА 6: Интеграция с реальными данными Tinkoff API
"""

import os
from tinkoff_api import check_api_connection, get_prices_with_fallback, get_real_prices, get_demo_prices

def test_tinkoff_integration():
    """Тестирует интеграцию с Tinkoff API"""
    
    print("🧪 ТЕСТ ШАГА 6: ИНТЕГРАЦИЯ С TINKOFF API")
    print("=" * 50)
    
    # Проверка переменной окружения
    token = os.getenv("TINKOFF_SANDBOX_TOKEN")
    print(f"🔑 TINKOFF_SANDBOX_TOKEN: {'✅ Настроен' if token else '❌ Отсутствует'}")
    
    if token:
        print(f"📝 Токен: {token[:10]}...")
    
    print("\n" + "-" * 30)
    
    # Проверка подключения к API
    print("🔗 Проверка подключения к Tinkoff API...")
    
    api_connected = check_api_connection()
    if api_connected:
        print("✅ Подключение к Tinkoff API: УСПЕШНО")
        
        # Тест получения реальных цен
        print("\n📊 Получение реальных цен...")
        real_prices = get_real_prices()
        
        if real_prices:
            print("✅ Реальные цены получены:")
            for ticker, price in real_prices.items():
                print(f"   • {ticker}: {price:.2f} ₽")
        else:
            print("❌ Не удалось получить реальные цены")
            
    else:
        print("⚠️ Подключение к Tinkoff API: НЕ УДАЛОСЬ")
        print("   Возможные причины:")
        print("   - Токен не настроен или неверный")
        print("   - Проблемы с сетью")
        print("   - API недоступен")
    
    print("\n" + "-" * 30)
    
    # Тест получения цен с fallback
    print("🔄 Тестирование функции получения цен с fallback...")
    
    prices = get_prices_with_fallback()
    if prices:
        print("✅ Цены получены (реальные или demo):")
        for ticker, price in prices.items():
            print(f"   • {ticker}: {price:.2f} ₽")
        
        # Определяем режим
        if api_connected:
            print("ℹ️  Режим: РЕАЛЬНЫЕ ДАННЫЕ")
        else:
            print("ℹ️  Режим: DEMO ДАННЫЕ")
    else:
        print("❌ Не удалось получить цены")
    
    print("\n" + "-" * 30)
    
    # Итоговый статус
    print("📋 ИТОГОВЫЙ СТАТУС:")
    
    if api_connected and real_prices:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        print("✅ Tinkoff API работает корректно")
        print("✅ Реальные цены получаются успешно")
        
        print("\n🚀 СЛЕДУЮЩИЕ ДЕЙСТВИЯ:")
        print("1. Перезапустите бота: python daily_plan_bot_ptb.py")
        print("2. Отправьте команду /prices - должны появиться реальные цены")
        print("3. Отправьте команду /status - должен показать ✅ для Tinkoff API")
        
        return True
        
    elif token and not api_connected:
        print("⚠️ ЧАСТИЧНЫЙ УСПЕХ")
        print("✅ Токен настроен")
        print("❌ Подключение к API не работает")
        
        print("\n🔧 РЕКОМЕНДАЦИИ:")
        print("1. Проверьте правильность токена")
        print("2. Убедитесь, что это токен для sandbox")
        print("3. Проверьте интернет-соединение")
        
        return False
        
    else:
        print("❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print("❌ Токен не настроен")
        
        print("\n🔧 НАСТРОЙКА:")
        print("1. Получите токен на https://developers.tinkoff.ru/")
        print("2. Добавьте в .env: TINKOFF_SANDBOX_TOKEN=ваш_токен")
        print("3. Перезапустите тест")
        
        return False

if __name__ == "__main__":
    test_tinkoff_integration()
