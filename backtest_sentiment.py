
import sqlite3
import collections
import pandas as pd
import os
import datetime as dt
import requests

DB = os.getenv("NEWS_DB", "db/news_cache.db")
conn = sqlite3.connect(DB)
rows = conn.execute("SELECT ticker,label FROM news").fetchall()

stats = collections.defaultdict(lambda: {"pos":0,"neg":0,"neu":0})
for ticker,label in rows:
    if label > 0:   stats[ticker]["pos"] += 1
    elif label < 0: stats[ticker]["neg"] += 1
    else:           stats[ticker]["neu"] += 1

for t,d in stats.items():
    d["N"]   = d["pos"]+d["neg"]+d["neu"]
    d["PnL"] = d["pos"]-d["neg"]

df = pd.DataFrame.from_dict(stats, orient="index")
df = df[["N","pos","neg","neu","PnL"]].sort_values("PnL", ascending=False)
pd.set_option("display.max_rows",None)
print("\n=== Sentiment Back-test ===")
print(df)

# === ОТПРАВКА В GOOGLE SHEETS ===
WEBHOOK_URL = os.getenv("SHEETS_WEBHOOK_URL")
TOKEN = os.getenv("SHEETS_TOKEN")

if WEBHOOK_URL and TOKEN:
    print("\n🔄 Отправляем результаты бэктеста в Google Sheets...")
    
    # Формируем данные для отправки
    backtest_rows = []
    timestamp = dt.datetime.utcnow().isoformat(timespec="seconds")
    
    for ticker, data in stats.items():
        row = [
            ticker,
            data["N"],      # общее количество
            data["pos"],    # позитивные
            data["neg"],    # негативные  
            data["neu"],    # нейтральные
            data["PnL"],    # P&L
            timestamp
        ]
        backtest_rows.append(row)
    
    payload = {
        "token": TOKEN,
        "tag": "backtest",
        "rows": backtest_rows
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=15)
        print(f"📊 Статус: {response.status_code}")
        print(f"📝 Ответ: {response.text}")
        
        if response.status_code == 200:
            print("✅ Данные бэктеста успешно отправлены в Google Sheets!")
        else:
            print(f"❌ Ошибка отправки: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка при отправке в Google Sheets: {e}")
else:
    print("⚠️ Google Sheets не настроен (нет WEBHOOK_URL или TOKEN)")
