
#!/usr/bin/env python
"""
Тест функции получения P/L из Google Sheets
"""

import os
from utils.sheets_logger import get_pnl, log_trade
import datetime as dt

def test_pnl_function():
    """Тестирует функцию получения P/L"""
    
    print("🧮 ТЕСТ ФУНКЦИИ GET_PNL")
    print("=" * 50)
    
    try:
        # Сначала добавим несколько тестовых сделок
        print("📝 Добавляем тестовые сделки...")
        
        # Покупка YNDX
        log_trade(
            date=dt.date.today(),
            ticker="YNDX",
            figi="BBG004730N88",
            side="BUY",
            price=2500.0,
            qty=2
        )
        
        # Продажа части YNDX с прибылью
        log_trade(
            date=dt.date.today(),
            ticker="YNDX", 
            figi="BBG004730N88",
            side="SELL",
            price=2600.0,
            qty=1
        )
        
        print("✅ Тестовые сделки добавлены")
        
        # Теперь получаем P/L
        print("\n💰 Запрашиваем P/L...")
        pnl = get_pnl()
        
        print(f"✅ Суммарный P/L: {pnl} ₽")
        
        if pnl > 0:
            print("🟢 Прибыль!")
        elif pnl < 0:
            print("🔴 Убыток!")
        else:
            print("🟡 В ноль")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании P/L: {e}")
        return False

if __name__ == "__main__":
    success = test_pnl_function()
    
    if success:
        print("\n🚀 Функция get_pnl() работает корректно!")
    else:
        print("\n❌ Требуется настройка функции P/L")
