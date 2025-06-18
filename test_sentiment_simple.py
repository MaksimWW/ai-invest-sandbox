
#!/usr/bin/env python
"""
🧪 ПРОСТОЙ ТЕСТ КОМАНДЫ /sentiment
==================================
Тестирование без сложных зависимостей Telegram
"""

import os
import sqlite3
import datetime as dt
from db.storage import insert

def simple_sentiment_test():
    """Простой тест логики команды /sentiment"""
    
    print("🚀 ПРОСТОЙ ТЕСТ КОМАНДЫ /sentiment")
    print("=" * 50)
    
    # 1) Добавляем тестовые данные
    print("📝 Добавляем тестовые новости...")
    
    now = dt.datetime.utcnow()
    test_data = [
        (now - dt.timedelta(hours=1), "SBER", "Сбербанк показал отличные результаты", 1, "test"),
        (now - dt.timedelta(hours=2), "SBER", "Аналитики повысили прогнозы по банку", 1, "test"),
        (now - dt.timedelta(hours=3), "SBER", "Проблемы в банковском секторе", -1, "test"),
        (now - dt.timedelta(hours=4), "SBER", "Нейтральные новости о рынке", 0, "test"),
        (now - dt.timedelta(hours=25), "SBER", "Старая новость", 1, "test"),  # За пределами 24ч
    ]
    
    for dt_val, ticker, headline, label, source in test_data:
        insert(dt_val.isoformat(timespec="seconds"), ticker, headline, label, source)
    
    print(f"✅ Добавлено {len(test_data)} тестовых записей")
    
    # 2) Тестируем запрос
    print("\n🔍 Тестируем запрос к базе данных...")
    
    ticker = "SBER"
    hours = 24
    
    try:
        db_path = os.getenv("NEWS_DB", "db/news_cache.db")
        db = sqlite3.connect(db_path)
        
        query = """
          SELECT dt, headline, label
          FROM   news
          WHERE  ticker = ? AND dt >= datetime('now', ? || ' hours')
          ORDER  BY dt DESC
          LIMIT  5
        """
        
        rows = db.execute(query, (ticker, -hours)).fetchall()
        db.close()
        
        print(f"📊 Найдено записей: {len(rows)}")
        
        if rows:
            def emoji(lbl):
                return {1:"👍", -1:"👎", 0:"⚪"}.get(lbl, "❓")
            
            print(f"\n📰 Результат для {ticker} за {hours}ч:")
            print("-" * 60)
            
            for i, (dt_str, headline, label) in enumerate(rows, 1):
                print(f"{i}. {emoji(label)} {headline}")
            
            # Имитируем ответ бота
            lines = [f"📰 *{ticker}* · {hours}ч\n"]
            for dt_str, headline, label in rows:
                lines.append(f"{emoji(label)} {headline[:120]}")
            
            bot_response = "\n".join(lines)
            
            print(f"\n🤖 Ответ бота:")
            print("-" * 60)
            print(bot_response)
            
            return True
        else:
            print(f"❌ Записей не найдено для {ticker}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка теста: {e}")
        return False

def test_different_scenarios():
    """Тестируем разные сценарии"""
    
    print("\n🧪 ТЕСТ РАЗНЫХ СЦЕНАРИЕВ")
    print("=" * 40)
    
    scenarios = [
        ("SBER", 12, "Тест за 12 часов"),
        ("SBER", 6, "Тест за 6 часов"),
        ("YNDX", 24, "Тест несуществующего тикера"),
    ]
    
    for ticker, hours, description in scenarios:
        print(f"\n📋 {description}: /sentiment {ticker} {hours}")
        
        try:
            db = sqlite3.connect(os.getenv("NEWS_DB", "db/news_cache.db"))
            query = """
              SELECT COUNT(*) as count
              FROM   news
              WHERE  ticker = ? AND dt >= datetime('now', ? || ' hours')
            """
            
            result = db.execute(query, (ticker, -hours)).fetchone()
            count = result[0] if result else 0
            db.close()
            
            if count > 0:
                print(f"   ✅ Найдено {count} записей")
            else:
                print(f"   📭 Записей не найдено")
                
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🎯 Запуск простого теста команды /sentiment\n")
    
    success = simple_sentiment_test()
    test_different_scenarios()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО")
        print("💡 Команда /sentiment готова к использованию в Telegram боте")
    else:
        print("⚠️ ТЕСТ НЕ ПРОШЕЛ")
        print("💡 Проверьте настройки базы данных")
    
    print("\n📱 Для тестирования в Telegram используйте:")
    print("   /sentiment SBER")
    print("   /sentiment SBER 12")
    print("   /sentiment YNDX 24")
