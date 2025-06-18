
#!/usr/bin/env python
"""
🧹 ОЧИСТКА ТЕСТОВЫХ ДАННЫХ
=========================
Удаляет все тестовые записи из базы данных
"""

import os
import sqlite3

def cleanup_test_data():
    """Удаляет тестовые записи из базы данных"""
    
    print("🧹 ОЧИСТКА ТЕСТОВЫХ ДАННЫХ")
    print("=" * 40)
    
    db_path = os.getenv("NEWS_DB", "db/news_cache.db")
    
    try:
        db = sqlite3.connect(db_path)
        cursor = db.cursor()
        
        # Удаляем тестовые заголовки
        cursor.execute("DELETE FROM news WHERE headline LIKE 'Тестовый заголовок%'")
        deleted_count = cursor.rowcount
        
        db.commit()
        db.close()
        
        print(f"✅ Удалено {deleted_count} тестовых записей")
        print("🎯 База данных очищена от тестовых данных")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка очистки: {e}")
        return False

if __name__ == "__main__":
    cleanup_test_data()
