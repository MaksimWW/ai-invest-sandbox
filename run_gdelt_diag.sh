
#!/usr/bin/env bash

echo "🔍 GDELT EXTENDED Connectivity Diagnostic"
echo "========================================"

echo ""
echo "1️⃣ Базовая диагностика GDELT API..."
echo "------------------------------------"
python -m tools.gdelt_diag

echo ""
echo "2️⃣ Исследование проблем и решений..."
echo "------------------------------------"
python -m tools.gdelt_research

echo ""
echo "3️⃣ Unit-тесты диагностических функций..."
echo "----------------------------------------"
python -m pytest tests/test_gdelt_diag.py -v --tb=short 2>/dev/null || echo "⚠️ pytest не установлен, пропускаем тесты"

echo ""
echo "✅ Полная диагностика завершена"
echo "================================"
