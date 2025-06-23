
#!/usr/bin/env python3
"""Анализ размера проекта - что занимает больше всего места"""

import os
import pathlib
from collections import defaultdict

def analyze_directory(path="."):
    """Анализирует размеры файлов и директорий"""
    
    # Словари для группировки
    by_extension = defaultdict(int)
    by_directory = defaultdict(int) 
    large_files = []
    
    total_size = 0
    
    for root, dirs, files in os.walk(path):
        # Пропускаем некоторые системные папки
        dirs[:] = [d for d in dirs if not d.startswith('.git')]
        
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                total_size += size
                
                # По расширениям
                ext = pathlib.Path(file).suffix.lower()
                if not ext:
                    ext = "(no extension)"
                by_extension[ext] += size
                
                # По директориям
                rel_root = os.path.relpath(root, path)
                if rel_root == ".":
                    rel_root = "(root)"
                by_directory[rel_root] += size
                
                # Большие файлы (>1MB)
                if size > 1024 * 1024:
                    large_files.append((file_path, size))
                    
            except (OSError, IOError):
                continue
    
    return {
        'total_size': total_size,
        'by_extension': dict(by_extension),
        'by_directory': dict(by_directory),
        'large_files': large_files
    }

def format_size(bytes_size):
    """Форматирует размер в человеко-читаемый вид"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def main():
    print("🔍 АНАЛИЗ РАЗМЕРА ПРОЕКТА")
    print("=" * 50)
    
    analysis = analyze_directory()
    
    print(f"\n📊 ОБЩИЙ РАЗМЕР: {format_size(analysis['total_size'])}")
    
    print(f"\n🗂️ ТОП-10 ДИРЕКТОРИЙ ПО РАЗМЕРУ:")
    print("-" * 40)
    sorted_dirs = sorted(analysis['by_directory'].items(), key=lambda x: x[1], reverse=True)
    for dirname, size in sorted_dirs[:10]:
        print(f"  {dirname:<25} {format_size(size):>10}")
    
    print(f"\n📄 ТОП-10 ТИПОВ ФАЙЛОВ ПО РАЗМЕРУ:")
    print("-" * 40)
    sorted_exts = sorted(analysis['by_extension'].items(), key=lambda x: x[1], reverse=True)
    for ext, size in sorted_exts[:10]:
        print(f"  {ext:<15} {format_size(size):>10}")
    
    print(f"\n🐘 БОЛЬШИЕ ФАЙЛЫ (>1MB):")
    print("-" * 40)
    if analysis['large_files']:
        sorted_files = sorted(analysis['large_files'], key=lambda x: x[1], reverse=True)
        for filepath, size in sorted_files[:15]:
            print(f"  {filepath:<40} {format_size(size):>10}")
    else:
        print("  Больших файлов не найдено")
    
    # Рекомендации по очистке
    print(f"\n💡 РЕКОМЕНДАЦИИ ПО ОЧИСТКЕ:")
    print("-" * 40)
    
    # Проверяем скриншоты
    screenshot_size = analysis['by_extension'].get('.png', 0)
    if screenshot_size > 10 * 1024 * 1024:  # >10MB
        print(f"  • Удалить скриншоты из attached_assets/ ({format_size(screenshot_size)})")
    
    # Проверяем кэши
    cache_indicators = ['.pyc', '.cache', '__pycache__']
    for indicator in cache_indicators:
        if indicator in analysis['by_directory'] or indicator in analysis['by_extension']:
            print(f"  • Очистить Python кэши")
            break
    
    # Проверяем бинарные файлы
    binary_size = analysis['by_directory'].get('tools/keydb/bin', 0)
    if binary_size > 5 * 1024 * 1024:  # >5MB
        print(f"  • Рассмотреть установку keydb через пакетный менеджер вместо бинарного файла")
    
    # Проверяем логи
    log_size = analysis['by_extension'].get('.log', 0)
    if log_size > 1024 * 1024:  # >1MB
        print(f"  • Очистить лог-файлы ({format_size(log_size)})")

if __name__ == "__main__":
    main()
