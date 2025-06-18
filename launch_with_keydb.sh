
#!/usr/bin/env bash
# 1) ensure KeyDB binary exists
bash tools/keydb_install.sh
# 2) start keydb if not running
if ! pgrep -f "keydb-server" > /dev/null; then
    tools/keydb/bin/keydb-server --daemonize yes \
      --save "" --appendonly no \
      --bind 127.0.0.1 --port 6379
    echo "🚀 KeyDB daemon started."
fi
# 3) start the original repl command
python daily_plan_bot.py
