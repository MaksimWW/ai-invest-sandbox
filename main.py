#!/usr/bin/env python
"""
🤖 Точка входа для daily_plan_bot
Запускает исправленную версию бота без проблемных зависимостей
"""

if __name__ == "__main__":
    import sys
    
    # Импортируем исправленную версию
    from daily_plan_bot_fixed import run_telegram_bot, run_daily_analysis
    
    if len(sys.argv) > 1 and sys.argv[1] == "analysis":
        print("🚀 Запуск ежедневного анализа...")
        run_daily_analysis()
    else:
        print("🚀 Запуск Telegram бота (исправленная версия)")
        run_telegram_bot()