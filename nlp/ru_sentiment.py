
from functools import lru_cache
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch, requests, datetime as dt

MODEL_NAME = "sismetanin/rubert-rusentiment"
LABELS = ["negative", "neutral", "positive"]

@lru_cache(maxsize=1)
def _load_model():
    tok = AutoTokenizer.from_pretrained(MODEL_NAME)
    mdl = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
    mdl.eval()
    return tok, mdl

def classify(text: str) -> str:
    tok, mdl = _load_model()
    inputs = tok(text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = mdl(**inputs).logits
    return LABELS[logits.argmax().item()]

# --- простейший RSS-граббер ТАСС (можно заменить) ---
def latest_news(ticker: str, hours: int = 24) -> list[str]:
    url = "https://tass.ru/rss/v2.xml"
    xml = requests.get(url, timeout=5).text
    items = xml.split("<item>")[1:]            # грубый парсинг
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    res = []
    for it in items[:100]:
        title = it.split("<title>")[1].split("</title>")[0]
        pub   = it.split("<pubDate>")[1].split("</pubDate>")[0]
        ts = dt.datetime.strptime(pub[:-6], "%a, %d %b %Y %H:%M:%S")
        if ts > cutoff and ticker.lower() in title.lower():
            res.append(title)
    return res
