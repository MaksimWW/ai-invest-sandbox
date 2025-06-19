#!/usr/bin/env python
"""
🤖 Точка входа для daily_plan_bot   (версия на python-telegram-bot v20)
— Если запущено с аргументом  analysis  → выполняется ежедневный анализ
— Иначе стартует Telegram-бот
"""

import sys

# ---------------- Telegram-бот (PTB v20) ----------------
from daily_plan_bot_ptb import run_bot as run_telegram_bot

# ---------------- Аналитика (оставляем прежнюю функцию) -
try:
    from daily_plan_bot_fixed import run_daily_analysis   # в этом модуле она была
except ImportError:
    # Если перенесёте run_daily_analysis в другой файл — поменяйте здесь импорт
    def run_daily_analysis():
        print("⚠️  Функция run_daily_analysis не найдена.")

# ---------------- Точка входа ---------------------------
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "analysis":
        print("🚀 Запуск ежедневного анализа…")
        run_daily_analysis()
    else:
        print("🚀 Запуск Telegram-бота (PTB v20)")
        run_telegram_bot()