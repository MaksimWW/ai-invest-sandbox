
#!/usr/bin/env python
"""
GDELT Diagnostic Tools
Минимальный набор функций для диагностики подключения к GDELT API
"""

import requests
import time
from datetime import datetime
from typing import List, Optional
import traceback


def ping_gdelt(timeout: int = 6) -> bool:
    """
    Проверяет доступность GDELT API через HEAD-запрос
    
    Returns:
        bool: True если API доступен (status 200-399), False иначе
    """
    url = "https://api.gdeltproject.org/api/v2/doc/docsearch"
    
    try:
        response = requests.head(url, timeout=timeout)
        success = 200 <= response.status_code < 400
        
        if success:
            print(f"✅ GDELT ping: {response.status_code}")
        else:
            print(f"⚠️ GDELT ping: {response.status_code}")
            
        return success
        
    except requests.exceptions.Timeout:
        print(f"⏰ GDELT ping: Timeout ({timeout}s)")
        return False
    except requests.exceptions.SSLError as e:
        print(f"🔒 GDELT ping: SSL Error - {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"🌐 GDELT ping: Connection Error - {e}")
        return False
    except Exception as e:
        print(f"❌ GDELT ping: Unexpected error - {type(e).__name__}: {e}")
        return False


def quick_search(query: str = "AAPL", maxrecords: int = 3, timeout: int = 8) -> List[str]:
    """
    Выполняет быстрый поиск в GDELT API
    
    Args:
        query: Поисковый запрос (тикер)
        maxrecords: Максимальное количество записей
        timeout: Таймаут в секундах
        
    Returns:
        List[str]: Список заголовков новостей
        
    Raises:
        Exception: При ошибках API или сети
    """
    url = "https://api.gdeltproject.org/api/v2/doc/docsearch"
    params = {
        "query": query,
        "maxrecords": maxrecords,
        "format": "json",
        "mode": "ArtList"
    }
    
    try:
        response = requests.get(url, params=params, timeout=timeout)
        
        if response.status_code != 200:
            raise Exception(f"HTTP {response.status_code}: {response.reason}")
            
        data = response.json()
        articles = data.get("artList", [])
        
        titles = []
        for article in articles:
            title = article.get("title", "")
            if title:
                titles.append(title)
                
        return titles
        
    except requests.exceptions.Timeout:
        raise Exception(f"Request timeout after {timeout}s")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Connection error: {e}")
    except requests.exceptions.JSONDecodeError:
        raise Exception("Invalid JSON response from GDELT API")
    except Exception as e:
        raise Exception(f"GDELT API error: {e}")


def diag_report():
    """
    Выполняет полную диагностику GDELT API и выводит отчет
    """
    print("=" * 60)
    print("🔍 GDELT API DIAGNOSTIC REPORT")
    print("=" * 60)
    
    # UTC время проверки
    utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"⏰ Время проверки: {utc_time}")
    print()
    
    try:
        # Проверка ping
        print("📡 Проверка доступности API...")
        start_time = time.time()
        ping_result = ping_gdelt(timeout=6)
        latency = (time.time() - start_time) * 1000
        
        if ping_result:
            print(f"✅ Статус: OK")
            print(f"⚡ Латентность: {latency:.1f} ms")
        else:
            print(f"❌ Статус: FAIL")
            print(f"⚡ Латентность: {latency:.1f} ms")
            
        print()
        
        # Пример поиска
        print("🔍 Тестовый поиск по 'GAZP'...")
        try:
            titles = quick_search("GAZP", maxrecords=3, timeout=8)
            
            if titles:
                print(f"✅ Найдено {len(titles)} заголовков:")
                for i, title in enumerate(titles, 1):
                    print(f"   {i}. {title[:80]}...")
            else:
                print("⚠️ Заголовки не найдены (может быть нормально)")
                
            # Показываем полный URL последнего запроса
            base_url = "https://api.gdeltproject.org/api/v2/doc/docsearch"
            full_url = f"{base_url}?query=GAZP&maxrecords=3&format=json&mode=ArtList"
            print(f"\n🔗 Последний запрос: {full_url}")
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА:")
        print(traceback.format_exc())
        
    print("=" * 60)


if __name__ == "__main__":
    diag_report()
