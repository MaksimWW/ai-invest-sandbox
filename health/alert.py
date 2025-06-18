
import os, time, threading, requests

_CHAT  = os.getenv("TELEGRAM_CHAT_ID")
_TOKEN = os.getenv("TELEGRAM_TOKEN")
_URL   = f"https://api.telegram.org/bot{_TOKEN}/sendMessage"
_lock  = threading.Lock()

_series_start = 0
_error_count  = 0

def register_error(tag: str):
    """Увеличивает счётчик ошибок и шлёт алерт при 3+ за 5 мин."""
    global _series_start, _error_count
    now = time.time()
    with _lock:
        if now - _series_start > 300:          # старее 5 мин — новая серия
            _series_start = now
            _error_count = 1
        else:
            _error_count += 1

        if _error_count == 3 and _CHAT and _TOKEN:
            txt = f"⚠️ {tag}: 3 ошибки RSS/NewsAPI подряд"
            requests.post(_URL, json={"chat_id": _CHAT, "text": txt})
