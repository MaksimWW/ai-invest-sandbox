
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

# --- RSS-граббер с несколькими источниками ---
RSS_FEEDS = [
    "https://tass.ru/rss/v2.xml",
    "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
]

def latest_news(ticker: str, hours: int = 24) -> list[str]:
    cutoff = dt.datetime.utcnow() - dt.timedelta(hours=hours)
    found = []
    for url in RSS_FEEDS:
        try:
            xml = requests.get(url, timeout=5).text
            for it in xml.split("<item>")[1:]:
                title = it.split("<title>")[1].split("</title>")[0]
                pub   = it.split("<pubDate>")[1].split("</pubDate>")[0]
                dt_pub = dt.datetime.strptime(pub[:-6], "%a, %d %b %Y %H:%M:%S")
                if dt_pub > cutoff and ticker.lower() in title.lower():
                    found.append(title)
        except Exception as e:
            print(f"⚠️ Ошибка обработки RSS {url}: {e}")
            continue
    return found
