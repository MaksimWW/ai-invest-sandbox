import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import openai
import redis
from functools import lru_cache
from health.metrics import record

# Конфигурация из переменных окружения
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_TEMP = float(os.getenv("LLM_TEMP", "0.0"))
LLM_MAXTOK = int(os.getenv("LLM_MAXTOK", "8"))
CACHE_HOURS = int(os.getenv("CACHE_HOURS", "24"))
LLM_OFF = bool(int(os.getenv("LLM_OFF", "0")))

# Redis клиент (с fallback на in-memory словарь)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    print("✅ Redis подключен")
except:
    pass  # Тихо переключаемся на in-memory кэш
    redis_client = {}

# SQLite база для постоянного хранения
DB_PATH = "news_cache.db"

def init_database():
    """Инициализирует SQLite базу для кэширования"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text_hash TEXT UNIQUE NOT NULL,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ticker TEXT,
            source TEXT DEFAULT 'llm'
        )
    ''')

    # Индекс для быстрого поиска по времени и тикеру
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp_ticker 
        ON sentiment_cache(timestamp, ticker)
    ''')

    conn.commit()
    conn.close()

def build_prompt(text: str) -> Dict[str, str]:
    """Строит оптимизированный промпт для LLM"""
    system_prompt = "Classify financial news sentiment: positive/negative/neutral. Reply with one word only."

    # Обрезаем текст до 100 символов для экономии токенов
    user_text = text[:100] + "..." if len(text) > 100 else text

    return {
        "system": system_prompt,
        "user": f"Text: {user_text}"
    }

def call_openai_sync(prompt: Dict[str, str], max_tokens: int = LLM_MAXTOK, temperature: float = LLM_TEMP) -> str:
    """Синхронный вызов OpenAI API"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY не настроен")

    if LLM_OFF:
        raise ValueError("LLM анализ отключен (LLM_OFF=1)")

    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Более экономная модель
            messages=[
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=10
        )

        usage = response.usage
        record("gpt_tokens", {
            "model":        response.model,
            "prompt":       usage.prompt_tokens,
            "completion":   usage.completion_tokens,
            "total":        usage.total_tokens
        })

        result = response.choices[0].message.content.strip().lower()

        # Нормализуем ответ
        if "positive" in result:
            return "positive"
        elif "negative" in result:
            return "negative"
        else:
            return "neutral"

    except Exception as e:
        print(f"❌ Ошибка OpenAI API: {e}")
        return "neutral"  # Fallback

def get_text_hash(text: str) -> str:
    """Генерирует хэш текста для кэширования"""
    import hashlib
    return hashlib.md5(text.encode()).hexdigest()

def cache_get(text_hash: str) -> Optional[Dict]:
    """Получает результат из кэша (Redis + SQLite)"""
    # Сначала проверяем Redis
    if isinstance(redis_client, dict):
        # In-memory fallback
        cached = redis_client.get(text_hash)
    else:
        try:
            cached = redis_client.get(f"sentiment:{text_hash}")
        except:
            cached = None

    if cached:
        try:
            return json.loads(cached)
        except:
            pass

    # Если Redis не сработал, проверяем SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ищем свежие записи (не старше CACHE_HOURS)
    cutoff = datetime.now() - timedelta(hours=CACHE_HOURS)

    cursor.execute('''
        SELECT sentiment, confidence, timestamp 
        FROM sentiment_cache 
        WHERE text_hash = ? AND timestamp > ?
        ORDER BY timestamp DESC LIMIT 1
    ''', (text_hash, cutoff.isoformat()))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            "sentiment": result[0],
            "confidence": result[1],
            "timestamp": result[2]
        }

    return None

def cache_set(text_hash: str, text: str, sentiment: str, confidence: float = 0.5, ticker: str = None):
    """Сохраняет результат в кэш (Redis + SQLite)"""
    data = {
        "sentiment": sentiment,
        "confidence": confidence,
        "timestamp": datetime.now().isoformat()
    }

    # Сохраняем в Redis
    if isinstance(redis_client, dict):
        # In-memory fallback
        redis_client[text_hash] = json.dumps(data)
    else:
        try:
            redis_client.setex(
                f"sentiment:{text_hash}", 
                timedelta(hours=CACHE_HOURS), 
                json.dumps(data)
            )
        except:
            pass

    # Сохраняем в SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT OR REPLACE INTO sentiment_cache 
            (text_hash, text, sentiment, confidence, ticker, source)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (text_hash, text, sentiment, confidence, ticker, 'llm'))

        conn.commit()
    except Exception as e:
        print(f"⚠️ Ошибка записи в SQLite: {e}")
    finally:
        conn.close()

def smart_classify(text: str, ticker: str = None) -> str:
    """Умная классификация с кэшированием"""
    if not text or not text.strip():
        return "neutral"

    text_hash = get_text_hash(text.strip())

    # Проверяем кэш
    cached = cache_get(text_hash)
    if cached:
        print(f"🔄 Кэш: {cached['sentiment']}")
        return cached["sentiment"]

    # Fallback на ключевые слова если LLM недоступен
    if LLM_OFF or not OPENAI_API_KEY:
        sentiment = fallback_classify(text)
        cache_set(text_hash, text, sentiment, 0.3, ticker)
        return sentiment

    # Вызываем LLM
    try:
        prompt = build_prompt(text)
        sentiment = call_openai_sync(prompt)

        print(f"🤖 LLM: {sentiment}")
        cache_set(text_hash, text, sentiment, 0.8, ticker)
        return sentiment

    except Exception as e:
        print(f"❌ LLM недоступен: {e}")
        sentiment = fallback_classify(text)
        cache_set(text_hash, text, sentiment, 0.3, ticker)
        return sentiment

def fallback_classify(text: str) -> str:
    """Fallback классификация по ключевым словам"""
    text_lower = text.lower()

    positive_words = [
        'рост', 'прибыль', 'доход', 'выросли', 'увелич', 'повыш', 'улучш',
        'rise', 'gain', 'profit', 'increase', 'growth', 'up', 'strong', 'beat'
    ]

    negative_words = [
        'падение', 'убыток', 'снизил', 'упали', 'кризис', 'уменьш', 'потер',
        'decline', 'loss', 'drop', 'fall', 'down', 'weak', 'miss', 'disappoint'
    ]

    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def get_sentiment_score_from_cache(ticker: str, hours: int = 24, force_refresh: bool = False) -> int:
    """Получить оценку настроения из кэша SQLite, если данные свежие"""

    # Если принудительное обновление - пропускаем кэш
    if force_refresh:
        print(f"🔄 Принудительное обновление для {ticker}")
        return 0

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Ищем записи за указанный период
        cutoff = datetime.now() - timedelta(hours=hours)

        cursor.execute('''
            SELECT sentiment FROM sentiment_cache 
            WHERE timestamp > ? AND (ticker = ? OR text LIKE ?)
            ORDER BY timestamp DESC
        ''', (cutoff.isoformat(), ticker, f'%{ticker}%'))

        results = cursor.fetchall()
        conn.close()

        if not results:
            print(f"📊 Кэш пуст для {ticker}")
            return 0

        # Подсчитываем score
        score = 0
        for (sentiment,) in results:
            if sentiment == "positive":
                score += 1
            elif sentiment == "negative":
                score -= 1

        print(f"📊 Настроение {ticker}: {score} (из {len(results)} новостей в кэше)")
        return score

    except Exception as e:
        print(f"Ошибка при получении score из кэша: {e}")
        return 0

def get_cache_stats() -> Dict:
    """Статистика кэша"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Общее количество записей
    cursor.execute("SELECT COUNT(*) FROM sentiment_cache")
    total = cursor.fetchone()[0]

    # Записи за последние 24 часа
    cutoff = datetime.now() - timedelta(hours=24)
    cursor.execute("SELECT COUNT(*) FROM sentiment_cache WHERE timestamp > ?", (cutoff.isoformat(),))
    recent = cursor.fetchone()[0]

    # Записи по источникам
    cursor.execute("SELECT source, COUNT(*) FROM sentiment_cache GROUP BY source")
    by_source = dict(cursor.fetchall())

    conn.close()

    return {
        "total_entries": total,
        "recent_24h": recent,
        "by_source": by_source
    }

# Инициализируем базу при импорте
init_database()