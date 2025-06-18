
import os
import datetime as dt
import json
import threading

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
