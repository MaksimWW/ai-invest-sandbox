
import sqlite3
import collections
import pandas as pd
import os

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
