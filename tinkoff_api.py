
#!/usr/bin/env python
"""
Модуль для работы с Tinkoff Invest API
Получение реальных цен акций и информации об инструментах
"""

import os
from tinkoff.invest import Client
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Токен из переменных окружения
TINKOFF_TOKEN = os.getenv("TINKOFF_SANDBOX_TOKEN")

# FIGI инструментов для отслеживания
INSTRUMENTS = {
    "YNDX": "BBG004730N88",  # Яндекс
    "FXIT": "BBG00Y91R9T3",  # Fix Price
    "GAZP": "BBG004730RP0",  # Газпром
    "SBER": "BBG0047315Y7",  # Сбербанк
}

# Обратная карта для совместимости с другими модулями
FIGI_MAP = {
    "YNDX": "BBG004730N88",
    "FXIT": "BBG00Y91R9T3", 
    "GAZP": "BBG004730RP0",
    "SBER": "BBG0047315Y7",
    "LKOH": "BBG004730ZJ9",
    "NVDA": "BBG000BBJQV0",
    "AMD":  "BBG000BBQCY0",
}

def check_api_connection() -> bool:
    """Проверяет подключение к Tinkoff API"""
    if not TINKOFF_TOKEN:
        return False
    
    try:
        with Client(TINKOFF_TOKEN, app_name="ai-invest-bot") as client:
            # Простая проверка - пробуем получить цену одного инструмента
            test_figi = "BBG004730N88"  # YNDX
            response = client.market_data.get_last_prices(figi=[test_figi])
            return len(response.last_prices) > 0
    except Exception as e:
        logger.error(f"Ошибка подключения к Tinkoff API: {e}")
        return False

def get_real_prices() -> Dict[str, float]:
    """Получает реальные цены акций через Tinkoff API"""
    if not TINKOFF_TOKEN:
        logger.warning("TINKOFF_TOKEN не настроен")
        return {}
    
    prices = {}
    
    try:
        with Client(TINKOFF_TOKEN, app_name="ai-invest-bot") as client:
            # Получаем последние цены для всех инструментов
            figis = list(INSTRUMENTS.values())
            response = client.market_data.get_last_prices(figi=figis)
            
            for last_price in response.last_prices:
                figi = last_price.figi
                price = last_price.price
                
                # Конвертируем цену в рубли
                price_rub = price.units + price.nano / 1_000_000_000
                
                # Находим тикер по FIGI
                for ticker, instrument_figi in INSTRUMENTS.items():
                    if instrument_figi == figi:
                        prices[ticker] = price_rub
                        break
                        
        logger.info(f"Получены цены для {len(prices)} инструментов")
        return prices
        
    except Exception as e:
        logger.error(f"Ошибка получения цен: {e}")
        return {}

def get_demo_prices() -> Dict[str, float]:
    """Возвращает демо цены для тестирования"""
    return {
        "YNDX": 2450.50,
        "FXIT": 1180.25,
        "GAZP": 180.20,
        "SBER": 250.15
    }

def get_prices_with_fallback() -> Dict[str, float]:
    """Получает цены с fallback на демо данные"""
    if not TINKOFF_TOKEN:
        logger.info("Используем DEMO цены - токен не настроен")
        return get_demo_prices()
    
    real_prices = get_real_prices()
    
    if not real_prices:
        logger.warning("Не удалось получить реальные цены, используем DEMO")
        return get_demo_prices()
    
    logger.info("Используем реальные цены из Tinkoff API")
    return real_prices

def format_price_change(current_price: float, demo_mode: bool = False) -> str:
    """Форматирует изменение цены (пока заглушка)"""
    if demo_mode:
        # Для демо режима генерируем случайные изменения
        import random
        change = random.uniform(-2.0, 2.0)
        if change > 0:
            return f"📈 (+{change:.1f}%)"
        else:
            return f"📉 ({change:.1f}%)"
    else:
        # Для реальных данных пока не реализовано
        return "📊"

if __name__ == "__main__":
    # Тест модуля
    print("🧪 Тестирование Tinkoff API модуля")
    print("-" * 40)
    
    # Проверка подключения
    if check_api_connection():
        print("✅ Подключение к API: OK")
    else:
        print("❌ Подключение к API: FAILED")
    
    # Получение цен
    prices = get_prices_with_fallback()
    print(f"\n📊 Полученные цены:")
    for ticker, price in prices.items():
        print(f"• {ticker}: {price:.2f} ₽")
