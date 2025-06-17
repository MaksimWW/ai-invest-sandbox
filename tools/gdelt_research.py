
#!/usr/bin/env python
"""
GDELT Research Tool
Поиск информации о проблемах доступности GDELT API
"""

import requests
import time
from datetime import datetime, timedelta
import json


def check_gdelt_github():
    """Проверяет GitHub репозиторий GDELT на issue"""
    print("🐙 Проверка GitHub репозитория GDELT...")
    
    github_repos = [
        "https://api.github.com/repos/linwoodc3/gdeltPyR/issues",
        "https://api.github.com/repos/alex9smith/gdelt-doc-api/issues"
    ]
    
    for repo_url in github_repos:
        try:
            response = requests.get(repo_url, timeout=10)
            if response.status_code == 200:
                issues = response.json()
                recent_issues = [
                    issue for issue in issues[:10] 
                    if "api" in issue.get("title", "").lower() or 
                       "timeout" in issue.get("title", "").lower() or
                       "connection" in issue.get("title", "").lower()
                ]
                
                if recent_issues:
                    print(f"   📋 Найдены связанные issue в {repo_url.split('/')[-2]}:")
                    for issue in recent_issues[:3]:
                        print(f"      • {issue['title'][:60]}...")
                        print(f"        {issue['html_url']}")
                else:
                    print(f"   ✅ Нет связанных issue в {repo_url.split('/')[-2]}")
                    
        except Exception as e:
            print(f"   ❌ Ошибка доступа к {repo_url}: {e}")


def check_gdelt_alternatives():
    """Проверяет альтернативные методы доступа к GDELT"""
    print("🔄 Поиск альтернативных методов доступа...")
    
    # Проверяем raw data endpoints
    raw_endpoints = [
        "http://data.gdeltproject.org/gdeltv2/",
        "http://data.gdeltproject.org/gdeltv3/",
        "https://blog.gdeltproject.org/",
        "http://data.gdeltproject.org/api-documentation/"
    ]
    
    for endpoint in raw_endpoints:
        try:
            response = requests.get(endpoint, timeout=8)
            if response.status_code == 200:
                print(f"   ✅ {endpoint} - Доступен")
            else:
                print(f"   ⚠️ {endpoint} - HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - {type(e).__name__}")


def check_working_examples():
    """Ищет рабочие примеры использования GDELT API"""
    print("💡 Тестирование известных рабочих примеров...")
    
    # Примеры запросов из документации
    working_examples = [
        {
            "name": "Базовый поиск по ключевому слову",
            "url": "https://api.gdeltproject.org/api/v2/doc/docsearch",
            "params": {"query": "climate change", "maxrecords": 1, "format": "json"}
        },
        {
            "name": "Поиск с фильтром по языку",
            "url": "https://api.gdeltproject.org/api/v2/doc/docsearch", 
            "params": {"query": "putin", "format": "json", "maxrecords": 1, "sourcelang": "english"}
        },
        {
            "name": "TV News Archive",
            "url": "https://api.gdeltproject.org/api/v2/tv/tv",
            "params": {"query": "trump", "format": "json", "maxrecords": 1}
        }
    ]
    
    for example in working_examples:
        print(f"   🧪 {example['name']}...")
        
        try:
            # Пробуем разные методы
            methods = [
                {"verify": True, "timeout": 10},
                {"verify": False, "timeout": 15},
            ]
            
            success = False
            for method in methods:
                try:
                    response = requests.get(
                        example["url"],
                        params=example["params"],
                        **method
                    )
                    
                    if response.status_code == 200:
                        print(f"      ✅ Успех! Статус: {response.status_code}")
                        
                        # Пробуем парсить JSON
                        try:
                            data = response.json()
                            if isinstance(data, dict):
                                keys = list(data.keys())[:3]
                                print(f"         📋 Ключи JSON: {keys}")
                        except:
                            print(f"         📄 Размер ответа: {len(response.content)} байт")
                        
                        success = True
                        break
                        
                except Exception as e:
                    continue
            
            if not success:
                print(f"      ❌ Все методы недоступны")
                
        except Exception as e:
            print(f"      ❌ Ошибка: {type(e).__name__}")


def test_gdelt_mirrors():
    """Тестирует возможные зеркала или CDN GDELT"""
    print("🪞 Поиск зеркал и CDN endpoints...")
    
    # Возможные альтернативные домены
    alternative_domains = [
        "api.gdeltproject.org",
        "www.gdeltproject.org", 
        "blog.gdeltproject.org",
        "data.gdeltproject.org"
    ]
    
    for domain in alternative_domains:
        print(f"   🌐 Тестируем {domain}...")
        
        try:
            # Простой ping
            response = requests.get(f"http://{domain}", timeout=8)
            print(f"      ✅ HTTP доступен: {response.status_code}")
            
            # Пробуем HTTPS
            try:
                https_response = requests.get(f"https://{domain}", timeout=8)
                print(f"      🔒 HTTPS доступен: {https_response.status_code}")
            except:
                print(f"      ❌ HTTPS недоступен")
                
        except Exception as e:
            print(f"      ❌ Недоступен: {type(e).__name__}")


def suggest_solutions():
    """Предлагает возможные решения"""
    print("💡 РЕКОМЕНДАЦИИ ПО РЕШЕНИЮ ПРОБЛЕМ:")
    print("-" * 50)
    
    solutions = [
        {
            "problem": "Таймаут соединения",
            "solutions": [
                "Увеличить timeout до 30+ секунд",
                "Использовать retry механизм с экспоненциальной задержкой",
                "Переключиться на HTTP вместо HTTPS",
                "Отключить SSL верификацию временно"
            ]
        },
        {
            "problem": "SSL/TLS ошибки", 
            "solutions": [
                "Добавить verify=False в requests",
                "Обновить certifi: pip install --upgrade certifi",
                "Использовать HTTP endpoint",
                "Настроить custom SSL context"
            ]
        },
        {
            "problem": "DNS проблемы",
            "solutions": [
                "Изменить DNS на 8.8.8.8 или 1.1.1.1",
                "Добавить IP в /etc/hosts",
                "Использовать прямой IP вместо домена",
                "Проверить firewall настройки"
            ]
        },
        {
            "problem": "Блокировка IP/User-Agent",
            "solutions": [
                "Изменить User-Agent на браузерный",
                "Добавить случайные задержки между запросами",
                "Использовать ротацию User-Agent",
                "Попробовать через VPN/proxy"
            ]
        },
        {
            "problem": "Временная недоступность API",
            "solutions": [
                "Проверить статус на blog.gdeltproject.org",
                "Реализовать fallback на кэш",
                "Использовать альтернативные источники данных",
                "Настроить мониторинг доступности"
            ]
        }
    ]
    
    for i, item in enumerate(solutions, 1):
        print(f"\n{i}. 🚨 {item['problem']}")
        for solution in item['solutions']:
            print(f"   • {solution}")


def main():
    """Основная функция исследования"""
    print("🔬 ИССЛЕДОВАНИЕ ПРОБЛЕМ GDELT API")
    print("=" * 60)
    
    print(f"⏰ Время: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # 1. GitHub issues
    check_gdelt_github()
    print()
    
    # 2. Альтернативные endpoints  
    check_gdelt_alternatives()
    print()
    
    # 3. Рабочие примеры
    check_working_examples()
    print()
    
    # 4. Зеркала
    test_gdelt_mirrors()
    print()
    
    # 5. Решения
    suggest_solutions()
    
    print("\n" + "=" * 60)
    print("🏁 Исследование завершено")


if __name__ == "__main__":
    main()
