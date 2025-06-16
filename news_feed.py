"""
news_feed.py  –   агрегатор англоязычных новостей
-------------------------------------------------
fetch_news(ticker: str, hours: int = 24) -> list[str]
"""
import os, datetime as dt, requests

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

def _newsapi_query(q, from_dt):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q"      : q,
        "language": "en",
        "sortBy" : "publishedAt",
        "from"   : from_dt.isoformat(timespec="seconds"),
        "apiKey" : NEWSAPI_KEY,
        "pageSize": 100,
    }
    r = requests.get(url, params=params, timeout=6)
    r.raise_for_status()
    return [a["title"] for a in r.json().get("articles", [])]

def _gdelt_query(q, from_dt):
    # GDELT 2.0 Events API Verbatim
    since = int(from_dt.timestamp())
    url = ("https://api.gdeltproject.org/api/v2/doc/docsearch"
           f"?query={q}&filter=SourceCommonName:english&maxrecords=100"
           f"&format=json&mode=ArtList&filter=PublishDate>{since}")

    # Попытаемся подключиться 3 раза с увеличивающимися паузами
    for attempt in range(3):
        try:
            print(f"🔄 GDELT попытка {attempt + 1}/3...")
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            
            data = r.json()
            articles = data.get("artList", [])
            print(f"✅ GDELT: найдено {len(articles)} новостей")
            return [item["title"] for item in articles]
            
        except requests.exceptions.Timeout:
            print(f"⏰ GDELT таймаут на попытке {attempt + 1}")
        except requests.exceptions.ConnectionError:
            print(f"🌐 GDELT проблема соединения на попытке {attempt + 1}")
        except Exception as e:
            print(f"❌ GDELT ошибка на попытке {attempt + 1}: {type(e).__name__}")
            
        if attempt < 2:  # Не последняя попытка
            import time
            sleep_time = (attempt + 1) * 3  # 3, 6 секунд
            print(f"⏳ Пауза {sleep_time} сек перед повтором...")
            time.sleep(sleep_time)
    
    print("❌ GDELT недоступен, продолжаем без него")
    return []

def fetch_news(ticker: str, hours: int = 24) -> list[str]:
    """Возвращает список англ. заголовков за последние `hours` часов."""
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    news = []
    
    # NewsAPI
    if NEWSAPI_KEY:
        print(f"📰 Запрашиваем NewsAPI для {ticker}...")
        newsapi_results = _newsapi_query(ticker, cutoff)
        news += newsapi_results
        print(f"✅ NewsAPI: найдено {len(newsapi_results)} новостей")
    else:
        print("⚠️ NewsAPI не настроен (нет NEWSAPI_KEY)")
    
    # GDELT
    gdelt_results = _gdelt_query(ticker, cutoff)
    news += gdelt_results
    
    print(f"📊 Итого для {ticker}: {len(news)} новостей (NewsAPI: {len(news) - len(gdelt_results)}, GDELT: {len(gdelt_results)})")
    return news