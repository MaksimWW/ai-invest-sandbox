
#!/usr/bin/env python3
"""
🛑 ОСТАНОВКА ВСЕХ ЭКЗЕМПЛЯРОВ БОТА
=====================================
Останавливает все процессы Python с ботами
"""

import os
import signal
import psutil
import time

def kill_bot_processes():
    """Находит и останавливает все процессы с ботами"""
    
    print("🔍 Поиск запущенных экземпляров бота...")
    
    killed_count = 0
    bot_files = [
        'daily_plan_bot_ptb.py',
        'daily_plan_bot.py', 
        'daily_plan_bot_fixed.py',
        'daily_plan_bot_mock.py',
        'main.py'
    ]
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                # Проверяем, является ли это Python процессом с нашим ботом
                if 'python' in cmdline[0].lower():
                    for bot_file in bot_files:
                        if any(bot_file in cmd for cmd in cmdline):
                            print(f"🔴 Найден процесс: PID {proc.info['pid']} - {' '.join(cmdline)}")
                            try:
                                proc.terminate()  # Мягкая остановка
                                proc.wait(timeout=3)  # Ждем 3 секунды
                                print(f"✅ Процесс {proc.info['pid']} остановлен")
                                killed_count += 1
                            except psutil.TimeoutExpired:
                                # Если не остановился, принудительно убиваем
                                proc.kill()
                                print(f"🔥 Процесс {proc.info['pid']} принудительно завершен")
                                killed_count += 1
                            except Exception as e:
                                print(f"❌ Ошибка остановки процесса {proc.info['pid']}: {e}")
                            break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            # Процесс уже завершился или нет доступа
            pass
    
    if killed_count > 0:
        print(f"🛑 Остановлено процессов: {killed_count}")
        print("⏱️ Ждем 3 секунды для полной остановки...")
        time.sleep(3)
    else:
        print("✅ Активных экземпляров бота не найдено")
    
    return killed_count

if __name__ == "__main__":
    print("🛑 ОСТАНОВКА ВСЕХ БОТОВ")
    print("=" * 30)
    
    killed = kill_bot_processes()
    
    print("\n🎉 Готово!")
    print(f"📊 Остановлено экземпляров: {killed}")
    print("🚀 Теперь можно безопасно запустить нового бота")
