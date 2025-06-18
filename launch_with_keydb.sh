#!/usr/bin/env bash

echo "🔄 Stopping all existing bot processes..."
pkill -f "daily_plan_bot.py" || true
pkill -f "python.*daily_plan_bot" || true
pkill -f "keydb-server" || true
pkill -f "redis-server" || true

# Проверяем, что процессы действительно остановлены
echo "⏱️ Ждем полной остановки процессов..."
sleep 3

# Дополнительная проверка и принудительная остановка
if pgrep -f "daily_plan_bot" > /dev/null; then
    echo "🔥 Принудительная остановка зависших процессов..."
    pkill -9 -f "daily_plan_bot" || true
    sleep 2
fi

# 1) ensure KeyDB binary exists
bash tools/keydb_install.sh
# 2) start keydb if not running
if ! pgrep -f "keydb-server" > /dev/null; then
    echo "🚀 Starting KeyDB daemon..."
    tools/keydb/bin/keydb-server --daemonize yes \
      --save "" --appendonly no \
      --bind 0.0.0.0 --port 6379 --protected-mode no &
    echo "✅ KeyDB daemon started."
else
    echo "✅ KeyDB already running."
fi
# 3) start the original repl command
echo "🤖 Запускаем Telegram бота..."
python daily_plan_bot.py