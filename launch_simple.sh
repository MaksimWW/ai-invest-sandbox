
#!/usr/bin/env bash

echo "🛑 Остановка всех процессов бота..."
pkill -f "daily_plan_bot" || true
sleep 3

echo "🤖 Запуск Telegram бота..."
python daily_plan_bot.py
