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

    # Попытаемся подключиться 3 раза
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            return [item["title"] for item in r.json().get("artList", [])]
        except Exception as e:
            if attempt == 2:  # Последняя попытка
                print(f"GDELT API недоступен после 3 попыток: {e}")
                return []
            import time
            time.sleep(2)  # Пауза перед повтором
    return []

def fetch_news(ticker: str, hours: int = 24) -> list[str]:
    """Возвращает список англ. заголовков за последние `hours` часов."""
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    news = []
    if NEWSAPI_KEY:
        news += _newsapi_query(ticker, cutoff)
    news += _gdelt_query(ticker, cutoff)
    return news