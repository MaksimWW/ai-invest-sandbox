
import aiohttp
import async_timeout
import asyncio
import gzip
import os
import time
import cachetools
import datetime as dt
import functools
from health.metrics import record

RSS_FEEDS = {
    "moex_issuer": "https://www.moex.com/export/news.aspx?news=issuer&lang=ru",
    "interfax"   : "https://www.finmarket.ru/xml/news.xml",
    "tass"       : "https://tass.ru/rss/v2.xml",
    "rbc"        : "https://rssexport.rbc.ru/rbcnews/news/finance.rss",
    "kommersant" : "https://www.kommersant.ru/RSS/main.xml",
    "lenta"      : "https://lenta.ru/rss/news",
}

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
              "AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/125.0 Safari/537.36")

_CACHE = cachetools.TTLCache(maxsize=128, ttl=900)   # 15 мин

def _timeout_for(url: str) -> int:
    if "moex.com/export/news" in url:
        return 15          # тяжёлый XML
    return int(os.getenv("RSS_TIMEOUT", "6"))

async def _single_try(url: str, timeout: int):
    hdrs = {"User-Agent": BROWSER_UA,
            "Accept-Encoding": "gzip, deflate"}
    async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)) as sess:
        async with async_timeout.timeout(timeout + 2):
            async with sess.get(url, headers=hdrs, ssl=False) as r:
                raw = await r.read()
                if r.headers.get("Content-Encoding") == "gzip":
                    raw = gzip.decompress(raw)
                return raw.decode(r.charset or "utf-8", "ignore")

async def _fetch(url: str):
    # 0) cache hit
    if url in _CACHE:
        return _CACHE[url]

    timeout = _timeout_for(url)
    url_variant = url
    for attempt in (1, 2, 3):
        try:
            data = await _single_try(url_variant, timeout)
            if data:           # сохраняем только не-пустой результат
                _CACHE[url] = data
            return data
        except Exception:
            # first fail on Interfax https → retry http
            if attempt == 1 and "finmarket.ru" in url_variant and url_variant.startswith("https"):
                url_variant = url_variant.replace("https://", "http://")
            else:
                await asyncio.sleep(2 ** attempt)   # 2s, 4s
    return None

async def async_fetch_all(hours: int = 24, ticker: str = None, log_to_cache: bool = False):
    """
    Fetches RSS feeds and optionally logs headlines to news cache
    
    Args:
        hours: Hours to look back for news
        ticker: Ticker symbol for logging
        log_to_cache: Whether to log headlines to db/storage
    """
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    tasks  = [_fetch(u) for u in RSS_FEEDS.values()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    fails = sum(1 for r in results if not r or isinstance(r, Exception))
    record("rss_batch", {"total": len(results), "fails": fails})
    
    # Если требуется логирование в кэш новостей
    if log_to_cache and ticker:
        from db.storage import insert as log_news
        
        # Парсим заголовки из RSS результатов
        headlines = []
        for result in results:
            if result and not isinstance(result, Exception):
                # Простой парсинг заголовков (предполагаем RSS XML)
                if "<title>" in result:
                    import re
                    titles = re.findall(r'<title[^>]*>([^<]+)</title>', result)
                    headlines.extend(titles[:5])  # Берем первые 5 заголовков
        
        # Логируем найденные заголовки
        current_time = dt.datetime.utcnow().isoformat(timespec="seconds")
        for headline in headlines:
            if headline and ticker.upper() in headline.upper():
                log_news(
                    dt=current_time,
                    ticker=ticker,
                    headline=headline[:300],
                    label=0,  # Neutral по умолчанию, будет переопределено при анализе
                    source="rss",
                    confidence=0.3
                )
    
    return results
