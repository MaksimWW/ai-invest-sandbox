
#!/usr/bin/env bash
set -e
if [[ ! -d tools/keydb/bin ]]; then
    echo "🔄  Installing Redis server as KeyDB alternative..."
    # Используем стандартный Redis вместо KeyDB
    mkdir -p tools/keydb/bin
    
    # Проверяем наличие redis-server в системе
    if command -v redis-server >/dev/null 2>&1; then
        ln -sf $(which redis-server) tools/keydb/bin/keydb-server
        echo "✅  Redis server linked as keydb-server"
    else
        echo "❌  Redis not found in system. Installing via package manager..."
        # Для Nix окружения Replit
        nix-env -iA nixpkgs.redis
        ln -sf $(which redis-server) tools/keydb/bin/keydb-server
        echo "✅  Redis installed and linked as keydb-server"
    fi
fi
