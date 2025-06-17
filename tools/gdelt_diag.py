
#!/usr/bin/env python
"""
GDELT Diagnostic Tools - Extended Version
Тестирование различных методов подключения к GDELT API
"""

import requests
import time
import urllib3
from datetime import datetime
from typing import List, Optional, Dict, Any
import traceback
import ssl
import socket
from urllib.parse import urlencode
import json

# Отключаем предупреждения SSL для тестирования
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Различные endpoints GDELT для тестирования
GDELT_ENDPOINTS = {
    "main": "https://api.gdeltproject.org/api/v2/doc/docsearch",
    "alternative": "http://api.gdeltproject.org/api/v2/doc/docsearch",
    "docs": "https://api.gdeltproject.org/api/v2/doc/doc",
    "geo": "https://api.gdeltproject.org/api/v2/geo/geo",
    "tv": "https://api.gdeltproject.org/api/v2/tv/tv",
    "lastupdate": "http://data.gdeltproject.org/gdeltv2/lastupdate.txt"
}

# Различные User-Agent для тестирования
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Python-requests/2.28.1",
    "GDELT-Client/1.0",
    "Research-Bot/1.0"
]

# DNS серверы для тестирования
DNS_SERVERS = [
    "8.8.8.8",      # Google
    "1.1.1.1",      # Cloudflare
    "208.67.222.222", # OpenDNS
    "9.9.9.9"       # Quad9
]


def test_dns_resolution():
    """Тестирует разрешение DNS для GDELT"""
    print("🌐 Тестирование DNS разрешения...")
    
    hostnames = [
        "api.gdeltproject.org",
        "data.gdeltproject.org",
        "gdeltproject.org"
    ]
    
    for hostname in hostnames:
        try:
            ip = socket.gethostbyname(hostname)
            print(f"   ✅ {hostname} -> {ip}")
        except socket.gaierror as e:
            print(f"   ❌ {hostname} -> DNS Error: {e}")


def test_basic_connectivity():
    """Тестирует базовое сетевое соединение"""
    print("🔌 Тестирование базового соединения...")
    
    try:
        # Пробуем подключиться к порту 80 и 443
        for port in [80, 443]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(("api.gdeltproject.org", port))
            sock.close()
            
            if result == 0:
                print(f"   ✅ Порт {port} доступен")
            else:
                print(f"   ❌ Порт {port} недоступен")
                
    except Exception as e:
        print(f"   ❌ Ошибка соединения: {e}")


def test_with_different_sessions():
    """Тестирует различные конфигурации requests.Session"""
    print("🔧 Тестирование различных конфигураций сессий...")
    
    configs = [
        {
            "name": "Стандартная сессия",
            "verify": True,
            "timeout": 10,
            "headers": {}
        },
        {
            "name": "Без SSL проверки",
            "verify": False,
            "timeout": 15,
            "headers": {}
        },
        {
            "name": "С пользовательским User-Agent",
            "verify": True,
            "timeout": 10,
            "headers": {"User-Agent": USER_AGENTS[0]}
        },
        {
            "name": "HTTP/1.1 принудительно",
            "verify": True,
            "timeout": 10,
            "headers": {"Connection": "close"}
        }
    ]
    
    for config in configs:
        print(f"   🧪 {config['name']}...")
        
        try:
            session = requests.Session()
            session.verify = config["verify"]
            session.headers.update(config["headers"])
            
            response = session.head(
                GDELT_ENDPOINTS["main"],
                timeout=config["timeout"]
            )
            
            print(f"      ✅ Статус: {response.status_code}")
            
        except requests.exceptions.Timeout:
            print(f"      ⏰ Таймаут")
        except requests.exceptions.SSLError:
            print(f"      🔒 SSL ошибка")
        except requests.exceptions.ConnectionError:
            print(f"      🌐 Ошибка соединения")
        except Exception as e:
            print(f"      ❌ Другая ошибка: {type(e).__name__}")


def test_all_endpoints():
    """Тестирует все доступные endpoints GDELT"""
    print("📡 Тестирование всех endpoints GDELT...")
    
    for name, url in GDELT_ENDPOINTS.items():
        print(f"   🔍 {name}: {url}")
        
        try:
            response = requests.head(url, timeout=8, verify=False)
            print(f"      ✅ Статус: {response.status_code}")
            
            if response.status_code == 200:
                # Пробуем GET запрос для работающих endpoints
                try:
                    get_response = requests.get(url, timeout=8, verify=False)
                    content_length = len(get_response.content)
                    print(f"      📄 Размер ответа: {content_length} байт")
                except:
                    pass
                    
        except requests.exceptions.Timeout:
            print(f"      ⏰ Таймаут")
        except requests.exceptions.ConnectionError:
            print(f"      🌐 Ошибка соединения")
        except Exception as e:
            print(f"      ❌ {type(e).__name__}: {str(e)[:50]}...")


def test_alternative_formats():
    """Тестирует различные форматы запросов к GDELT"""
    print("📋 Тестирование альтернативных форматов запросов...")
    
    base_url = "https://api.gdeltproject.org/api/v2/doc/docsearch"
    
    test_params = [
        {
            "name": "JSON формат",
            "params": {"query": "AAPL", "format": "json", "maxrecords": 1}
        },
        {
            "name": "CSV формат", 
            "params": {"query": "AAPL", "format": "csv", "maxrecords": 1}
        },
        {
            "name": "HTML формат",
            "params": {"query": "AAPL", "format": "html", "maxrecords": 1}
        },
        {
            "name": "Без параметров",
            "params": {}
        }
    ]
    
    for test in test_params:
        print(f"   🧪 {test['name']}...")
        
        try:
            response = requests.get(
                base_url,
                params=test["params"],
                timeout=10,
                verify=False
            )
            
            print(f"      ✅ Статус: {response.status_code}")
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "unknown")
                print(f"      📄 Content-Type: {content_type}")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ Таймаут")
        except Exception as e:
            print(f"      ❌ {type(e).__name__}")


def test_proxy_methods():
    """Тестирует подключение через различные методы"""
    print("🔄 Тестирование альтернативных методов подключения...")
    
    # Тест с различными версиями HTTP
    print("   🌐 HTTP версии:")
    
    try:
        # HTTP/1.1
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter()
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        response = session.get(
            "http://api.gdeltproject.org/api/v2/doc/docsearch",
            timeout=10
        )
        print(f"      ✅ HTTP (без SSL): {response.status_code}")
        
    except Exception as e:
        print(f"      ❌ HTTP: {type(e).__name__}")


def ping_gdelt(timeout: int = 6) -> bool:
    """Улучшенная версия ping с дополнительной диагностикой"""
    print("📡 Расширенная проверка доступности GDELT API...")
    
    for endpoint_name, url in list(GDELT_ENDPOINTS.items())[:3]:
        print(f"   🔍 Тестируем {endpoint_name}: {url}")
        
        try:
            start_time = time.time()
            response = requests.head(url, timeout=timeout, verify=False)
            latency = (time.time() - start_time) * 1000
            
            success = 200 <= response.status_code < 400
            
            if success:
                print(f"      ✅ Статус: {response.status_code}, Латентность: {latency:.1f}ms")
                return True
            else:
                print(f"      ⚠️ Статус: {response.status_code}, Латентность: {latency:.1f}ms")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ Таймаут ({timeout}s)")
        except requests.exceptions.SSLError as e:
            print(f"      🔒 SSL ошибка: {str(e)[:50]}...")
        except requests.exceptions.ConnectionError as e:
            print(f"      🌐 Ошибка соединения: {str(e)[:50]}...")
        except Exception as e:
            print(f"      ❌ Неожиданная ошибка: {type(e).__name__}")
    
    return False


def quick_search(query: str = "AAPL", maxrecords: int = 3, timeout: int = 8) -> List[str]:
    """Улучшенная версия поиска с fallback endpoints"""
    
    # Пробуем разные endpoints и конфигурации
    search_configs = [
        {
            "url": "https://api.gdeltproject.org/api/v2/doc/docsearch",
            "verify": True,
            "name": "HTTPS с SSL"
        },
        {
            "url": "http://api.gdeltproject.org/api/v2/doc/docsearch", 
            "verify": False,
            "name": "HTTP без SSL"
        },
        {
            "url": "https://api.gdeltproject.org/api/v2/doc/docsearch",
            "verify": False,
            "name": "HTTPS без SSL верификации"
        }
    ]
    
    params = {
        "query": query,
        "maxrecords": maxrecords,
        "format": "json",
        "mode": "ArtList"
    }
    
    for config in search_configs:
        print(f"   🔄 Пробуем {config['name']}...")
        
        try:
            response = requests.get(
                config["url"],
                params=params,
                timeout=timeout,
                verify=config["verify"],
                headers={"User-Agent": USER_AGENTS[0]}
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("artList", [])
                
                titles = []
                for article in articles:
                    title = article.get("title", "")
                    if title:
                        titles.append(title)
                
                print(f"      ✅ Успех! Найдено {len(titles)} результатов")
                return titles
            else:
                print(f"      ❌ HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"      ⏰ Таймаут ({timeout}s)")
        except requests.exceptions.ConnectionError:
            print(f"      🌐 Ошибка соединения")
        except requests.exceptions.JSONDecodeError:
            print(f"      📄 Ошибка парсинга JSON")
        except Exception as e:
            print(f"      ❌ {type(e).__name__}: {str(e)[:30]}...")
    
    raise Exception(f"Все методы подключения к GDELT недоступны")


def check_gdelt_status():
    """Проверяет статус сервисов GDELT"""
    print("📊 Проверка статуса сервисов GDELT...")
    
    status_endpoints = [
        "http://data.gdeltproject.org/gdeltv2/lastupdate.txt",
        "http://data.gdeltproject.org/gdeltv2/masterfilelist.txt",
        "http://data.gdeltproject.org/gdeltv2/masterfilelist-translation.txt"
    ]
    
    for endpoint in status_endpoints:
        try:
            response = requests.get(endpoint, timeout=8)
            if response.status_code == 200:
                content = response.text[:100]
                print(f"   ✅ {endpoint.split('/')[-1]}: Доступен")
                print(f"      📄 Превью: {content.strip()}")
            else:
                print(f"   ❌ {endpoint.split('/')[-1]}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {endpoint.split('/')[-1]}: {type(e).__name__}")


def diag_report():
    """Выполняет полную расширенную диагностику GDELT API"""
    print("=" * 80)
    print("🔍 РАСШИРЕННАЯ ДИАГНОСТИКА GDELT API")
    print("=" * 80)
    
    # UTC время проверки
    utc_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"⏰ Время проверки: {utc_time}")
    print()
    
    try:
        # 1. DNS разрешение
        test_dns_resolution()
        print()
        
        # 2. Базовое соединение
        test_basic_connectivity()
        print()
        
        # 3. Статус сервисов
        check_gdelt_status()
        print()
        
        # 4. Тестирование всех endpoints
        test_all_endpoints()
        print()
        
        # 5. Различные конфигурации сессий
        test_with_different_sessions()
        print()
        
        # 6. Альтернативные форматы
        test_alternative_formats()
        print()
        
        # 7. Альтернативные методы
        test_proxy_methods()
        print()
        
        # 8. Основной ping тест
        print("🎯 ОСНОВНОЙ ТЕСТ ДОСТУПНОСТИ:")
        ping_result = ping_gdelt(timeout=10)
        print()
        
        # 9. Тест поиска
        print("🔍 ТЕСТ ПОИСКА:")
        try:
            titles = quick_search("GAZP", maxrecords=3, timeout=15)
            
            if titles:
                print(f"✅ Найдено {len(titles)} заголовков:")
                for i, title in enumerate(titles, 1):
                    print(f"   {i}. {title[:80]}...")
            else:
                print("⚠️ Заголовки не найдены")
                
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            
    except Exception as e:
        print(f"💥 КРИТИЧЕСКАЯ ОШИБКА:")
        print(traceback.format_exc())
        
    print("=" * 80)
    print("🏁 Диагностика завершена")
    print("=" * 80)


if __name__ == "__main__":
    diag_report()
