
#!/usr/bin/env python
"""
🧪 ТЕСТ КОМАНДЫ /sentiment
==========================
Локальное тестирование функции cmd_sentiment без Telegram API
"""

import os
import sqlite3
import datetime as dt
from db.storage import insert

def test_sentiment_command():
    """Тестируем команду /sentiment локально"""
    
    print("🧪 ТЕСТ КОМАНДЫ /sentiment")
    print("=" * 40)
    
    # 1) Вставляем тестовые данные
    print("📝 Добавляем тестовые новости...")
    
    now = dt.datetime.utcnow()
    test_news = [
        (now - dt.timedelta(hours=1), "SBER", "Сбербанк показывает рост на 5%", 1, "llm"),
        (now - dt.timedelta(hours=2), "SBER", "Аналитики повышают прогнозы по Сберу", 1, "llm"), 
        (now - dt.timedelta(hours=3), "SBER", "Проблемы в банковском секторе", -1, "llm"),
        (now - dt.timedelta(hours=4), "SBER", "Нейтральные новости о банке", 0, "llm"),
        (now - dt.timedelta(hours=5), "SBER", "Еще одна новость по Сберу", 1, "llm")
    ]
    
    for news_dt, ticker, headline, label, source in test_news:
        insert(news_dt.isoformat(timespec="seconds"), ticker, headline, label, source)
    
    print(f"✅ Добавлено {len(test_news)} тестовых новостей")
    
    # 2) Тестируем логику команды напрямую
    print("\n🔍 Тестируем логику команды...")
    
    ticker = "SBER"
    hours = 24
    
    try:
        db = sqlite3.connect(os.getenv("NEWS_DB", "db/news_cache.db"))
        query = """
          SELECT dt, headline, label
          FROM   news
          WHERE  ticker = ? AND dt >= datetime('now', ? || ' hours')
          ORDER  BY dt DESC
          LIMIT  5
        """
        rows = db.execute(query, (ticker, -hours)).fetchall()
        db.close()
        
        if not rows:
            print(f"❌ Новостей по {ticker} за {hours} ч нет.")
            return False
        
        def emoji(lbl):
            return {1:"👍", -1:"👎", 0:"⚪"}.get(lbl, "❓")
        
        print(f"\n📰 Результат команды /sentiment {ticker} {hours}:")
        print("-" * 50)
        print(f"📰 *{ticker}* · {hours}ч\n")
        
        for dt_str, hline, lbl in rows:
            print(f"{emoji(lbl)} {hline[:120]}")
        
        print(f"\n✅ Найдено {len(rows)} новостей")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_with_different_params():
    """Тестируем с разными параметрами"""
    
    print("\n🔄 ТЕСТ С РАЗНЫМИ ПАРАМЕТРАМИ")
    print("=" * 40)
    
    test_cases = [
        ("SBER", 12),
        ("SBER", 6), 
        ("NVDA", 24),  # несуществующий тикер
    ]
    
    for ticker, hours in test_cases:
        print(f"\n🧪 Тест: /sentiment {ticker} {hours}")
        
        try:
            db = sqlite3.connect(os.getenv("NEWS_DB", "db/news_cache.db"))
            query = """
              SELECT dt, headline, label
              FROM   news
              WHERE  ticker = ? AND dt >= datetime('now', ? || ' hours')
              ORDER  BY dt DESC
              LIMIT  5
            """
            rows = db.execute(query, (ticker, -hours)).fetchall()
            db.close()
            
            if not rows:
                print(f"📭 Новостей по {ticker} за {hours} ч нет.")
            else:
                print(f"📊 Найдено {len(rows)} новостей по {ticker}")
                
        except Exception as e:
            print(f"❌ Ошибка для {ticker}: {e}")

if __name__ == "__main__":
    print("🚀 Запуск тестов команды /sentiment")
    
    # Основной тест
    success = test_sentiment_command()
    
    if success:
        # Дополнительные тесты
        test_with_different_params()
        
        print("\n" + "=" * 50)
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
        print("📋 Теперь можете протестировать команду в Telegram:")
        print("   /sentiment SBER")
        print("   /sentiment SBER 12")
    else:
        print("\n❌ ТЕСТЫ НЕ ПРОЙДЕНЫ")
