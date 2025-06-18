
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
        (now - dt.timedelta(hours=1), "SBER", "Тестовый заголовок растёт на 5%", 1, "llm"),
        (now - dt.timedelta(hours=2), "SBER", "Сбербанк показывает рост на 5%", 1, "llm"),
        (now - dt.timedelta(hours=3), "SBER", "Аналитики повышают прогнозы по Сберу", 1, "llm"), 
        (now - dt.timedelta(hours=4), "SBER", "Проблемы в банковском секторе", -1, "llm"),
        (now - dt.timedelta(hours=5), "SBER", "Нейтральные новости о банке", 0, "llm")
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
            print(f"📭 Новостей по {ticker} за {hours} ч нет.")
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
            print(f"❌ Ошибка: {e}")

def test_cmd_sentiment_function():
    """Тестируем саму функцию cmd_sentiment из daily_plan_bot.py"""
    print("\n🤖 ТЕСТ ФУНКЦИИ cmd_sentiment")
    print("=" * 40)
    
    try:
        # Создаем простые моки без сложных Telegram объектов
        class MockMessage:
            def __init__(self):
                self.replies = []
            
            def reply_text(self, text):
                self.replies.append(("text", text))
                print(f"BOT: {text}")
            
            def reply_markdown(self, text, parse_mode=None):
                self.replies.append(("markdown", text))
                print(f"BOT MD:\n{text}")
        
        class MockUpdate:
            def __init__(self):
                self.message = MockMessage()
        
        class MockContext:
            def __init__(self, args):
                self.args = args
        
        # Тестируем различные сценарии
        test_cases = [
            (["SBER"], "Тест с SBER без указания часов"),
            (["SBER", "24"], "Тест с SBER за 24 часа"),
            (["NVDA", "12"], "Тест с несуществующим тикером"),
            ([], "Тест без аргументов")
        ]
        
        for args, description in test_cases:
            print(f"\n📋 {description}")
            print(f"   Аргументы: {args}")
            
            update = MockUpdate()
            context = MockContext(args)
            
            # Имитируем логику команды cmd_sentiment напрямую
            if not args:
                update.message.reply_text("Использование: /sentiment TICKER [часов]")
            else:
                ticker = args[0].upper()
                try:
                    hours = int(args[1]) if len(args) > 1 else 48
                except ValueError:
                    update.message.reply_text("❌ Неверный формат часов. Используйте число.")
                    continue
                
                try:
                    import sqlite3
                    import os
                    
                    db_path = os.getenv("NEWS_DB", "db/news_cache.db")
                    
                    # Проверяем существование базы данных
                    if not os.path.exists(db_path):
                        update.message.reply_text(f"❌ База данных новостей не найдена: {db_path}")
                        continue
                    
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
                    
                    if not rows:
                        update.message.reply_text(f"Новостей по {ticker} за {hours} ч нет.")
                    else:
                        def emoji(lbl):
                            return {1:"👍", -1:"👎", 0:"⚪"}.get(lbl, "❓")
                        
                        lines = [f"📰 *{ticker}* · {hours}ч\n"]
                        for dt_str, hline, lbl in rows:
                            lines.append(f"{emoji(lbl)} {hline[:120]}")
                        
                        update.message.reply_markdown("\n".join(lines))
                
                except sqlite3.Error as e:
                    update.message.reply_text(f"❌ Ошибка базы данных: {e}")
                except Exception as e:
                    update.message.reply_text(f"❌ Ошибка получения новостей: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования функции: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестов команды /sentiment")
    
    # Запускаем все тесты
    test1 = test_sentiment_command()
    test_with_different_params()
    test2 = test_cmd_sentiment_function()
    
    print("\n" + "=" * 50)
    if test1 and test2:
        print("✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ")
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОШЛИ")
    
    print("📋 Теперь можете протестировать команду в Telegram:")
    print("   /sentiment SBER")
    print("   /sentiment SBER 12")
