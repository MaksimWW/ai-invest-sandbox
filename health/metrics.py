
import os
import datetime as dt
import json
import threading
from health.alert import register_error

_LOG = os.getenv("METRICS_LOGFILE", "health.log")
_lock = threading.Lock()

def record(event: str, payload: dict):
    """Append single-line JSON record to health.log"""
    rec = {
        "ts": dt.datetime.utcnow().isoformat(timespec="seconds"),
        "event": event, **payload
    }
    with _lock, open(_LOG, "a") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    
    # Проверяем на ошибки и отправляем алерты
    if event == "rss_batch" and payload.get("fails", 0):
        if payload["fails"] > 0:
            register_error("rss_batch")

    if event == "newsapi_call" and payload.get("articles", 0) == 0:
        register_error("newsapi_call")
