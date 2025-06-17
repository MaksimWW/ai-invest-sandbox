
#!/usr/bin/env bash

echo "🔍 GDELT Connectivity Diagnostic"
echo "================================"

# Запуск диагностики
python -m tools.gdelt_diag

echo ""
echo "🧪 Запуск unit-тестов..."
echo "------------------------"

# Запуск тестов
python -m pytest tests/test_gdelt_diag.py -v --tb=short

echo ""
echo "✅ Диагностика завершена"
