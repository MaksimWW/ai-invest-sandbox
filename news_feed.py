"""Modified news_feed.py to disable GDELT functionality based on user request."""
import requests
import datetime as dt
import os

# Переменная для отключения GDELT (по умолчанию отключен)
GDELT_ENABLED = os.getenv("GDELT_ENABLED", "0") == "1"

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
    # GDELT 2.0 Events API с альтернативными endpoints
    since = int(from_dt.timestamp())

    # Список альтернативных endpoints
    endpoints = [
        f"https://api.gdeltproject.org/api/v2/doc/docsearch?query={q}&filter=SourceCommonName:english&maxrecords=100&format=json&mode=ArtList&filter=PublishDate>{since}",
        f"https://api.gdeltproject.org/api/v2/doc/docsearchsearch?query={q}&filter=SourceCommonName:english&maxrecords=100&format=json&mode=ArtList&filter=PublishDate>{since}"
    ]

    for endpoint_idx, url in enumerate(endpoints, 1):
        endpoint_name = "docsearch" if "docsearch?" in url else "docsearchsearch"
        print(f"🌐 Пробуем GDELT endpoint #{endpoint_idx} ({endpoint_name})...")

        # Одна попытка для каждого endpoint
        try:
            print(f"🔄 {endpoint_name} запрос...")
            r = requests.get(url, timeout=15)
            r.raise_for_status()

            data = r.json()
            articles = data.get("artList", [])
            print(f"✅ GDELT ({endpoint_name}): найдено {len(articles)} новостей")
            return [item["title"] for item in articles]

        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint_name} таймаут")
        except requests.exceptions.ConnectionError:
            print(f"🌐 {endpoint_name} проблема соединения")
        except Exception as e:
            print(f"❌ {endpoint_name} ошибка: {type(e).__name__}")

        print(f"❌ GDELT endpoint {endpoint_name} недоступен")

    print("❌ Все GDELT endpoints недоступны, продолжаем без него")
    return []

def fetch_news(ticker: str, hours: int = 24) -> list[str]:
    """Получить новости по тикеру из NewsAPI + GDELT + Yahoo Finance"""
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

    # GDELT - условно отключен
    if GDELT_ENABLED:
        print(f"🌐 Запрашиваем GDELT для {ticker}...")
        gdelt_results = _gdelt_query(ticker, cutoff)
        news += gdelt_results
        print(f"✅ GDELT: найдено {len(gdelt_results)} новостей")
    else:
        gdelt_results = []
        print("⚠️ GDELT отключен (используйте GDELT_ENABLED=1 для включения)")

    print(f"📊 Итого для {ticker}: {len(news)} новостей (NewsAPI: {len(news) - len(gdelt_results)}, GDELT: {len(gdelt_results)})")
    return news
`