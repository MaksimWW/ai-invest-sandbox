
import sqlite3
import os
import threading
import contextlib
from datetime import datetime

_PATH = os.getenv("NEWS_DB", "db/news_cache.db")
_lock = threading.Lock()

def _get():
    """Создает подключение к SQLite и таблицу если её нет"""
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(_PATH), exist_ok=True)
    
    conn = sqlite3.connect(_PATH, check_same_thread=False)
    conn.execute("""CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dt TEXT,
        ticker TEXT,
        headline TEXT,
        label INTEGER,
        source TEXT,
        confidence REAL DEFAULT 0.5,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    
    # Создаем индекс для быстрого поиска
    conn.execute("""CREATE INDEX IF NOT EXISTS idx_dt_ticker 
                   ON news(dt, ticker)""")
    
    conn.commit()
    return conn

_CONN = _get()

def insert(dt: str, ticker: str, headline: str, label: int, source: str, confidence: float = 0.5):
    """Записывает новость в кэш"""
    with _lock:
        try:
            _CONN.execute(
                "INSERT INTO news(dt, ticker, headline, label, source, confidence) VALUES(?,?,?,?,?,?)",
                (dt, ticker, headline[:300], label, source, confidence)
            )
            _CONN.commit()
        except Exception as e:
            print(f"⚠️ Ошибка записи в news cache: {e}")

def get_recent_news(ticker: str = None, hours: int = 24):
    """Получает недавние новости из кэша"""
    with _lock:
        query = "SELECT dt, ticker, headline, label, source, confidence FROM news WHERE datetime(dt) > datetime('now', '-{} hours')".format(hours)
        params = []
        
        if ticker:
            query += " AND ticker = ?"
            params.append(ticker)
            
        query += " ORDER BY dt DESC"
        
        cursor = _CONN.execute(query, params)
        return cursor.fetchall()

def get_stats():
    """Статистика кэша новостей"""
    with _lock:
        cursor = _CONN.execute("SELECT COUNT(*) FROM news")
        total = cursor.fetchone()[0]
        
        cursor = _CONN.execute("SELECT source, COUNT(*) FROM news GROUP BY source")
        by_source = dict(cursor.fetchall())
        
        cursor = _CONN.execute("SELECT COUNT(*) FROM news WHERE datetime(dt) > datetime('now', '-24 hours')")
        recent_24h = cursor.fetchone()[0]
        
        return {
            "total_entries": total,
            "recent_24h": recent_24h,
            "by_source": by_source
        }
