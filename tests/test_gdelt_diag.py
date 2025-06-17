
#!/usr/bin/env python
"""
Unit tests for GDELT diagnostic tools
"""

import pytest
from tools.gdelt_diag import ping_gdelt, quick_search


@pytest.mark.timeout(10)
def test_ping():
    """Тест проверки доступности GDELT API"""
    result = ping_gdelt(timeout=6)
    
    if not result:
        pytest.skip("GDELT API недоступен - пропускаем тест")
        
    assert result is True, "GDELT API должен быть доступен"


@pytest.mark.timeout(10) 
def test_quick_search():
    """Тест быстрого поиска в GDELT API"""
    try:
        results = quick_search("GAZP", maxrecords=3, timeout=8)
        
        # Проверяем, что вернулся список (может быть пустым)
        assert isinstance(results, list), "quick_search должен возвращать список"
        
        # Если есть результаты, проверяем их тип
        if results:
            assert all(isinstance(title, str) for title in results), "Все элементы должны быть строками"
            print(f"✅ Найдено {len(results)} заголовков")
        else:
            print("ℹ️ Результаты поиска пусты (может быть нормально)")
            
    except Exception as e:
        # Если GDELT недоступен, тест должен завершиться с понятным сообщением
        pytest.fail(f"GDELT unavailable: {e}")


@pytest.mark.timeout(15)
def test_integration():
    """Интеграционный тест: ping + search"""
    # Сначала ping
    ping_ok = ping_gdelt(timeout=5)
    
    if not ping_ok:
        pytest.skip("GDELT ping failed - пропускаем интеграционный тест")
    
    # Затем поиск
    try:
        results = quick_search("AAPL", maxrecords=2, timeout=8)
        assert isinstance(results, list)
        print(f"✅ Интеграционный тест прошел: ping OK, search вернул {len(results)} результатов")
        
    except Exception as e:
        pytest.fail(f"Интеграционный тест failed: {e}")


if __name__ == "__main__":
    # Запуск тестов напрямую
    import sys
    import subprocess
    
    # Запускаем pytest для этого файла
    result = subprocess.run([
        sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"
    ])
    
    sys.exit(result.returncode)
