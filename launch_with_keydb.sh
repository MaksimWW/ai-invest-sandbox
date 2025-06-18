
#!/usr/bin/env bash

echo "🔄 Stopping all existing bot processes..."
pkill -f "daily_plan_bot.py" || true
pkill -f "python.*daily_plan_bot" || true
sleep 3

echo "🔄 Checking for Redis/KeyDB server..."

# Проверяем, запущен ли уже Redis на порту 6379
if netstat -tuln 2>/dev/null | grep -q ":6379 "; then
    echo "✅ Redis/KeyDB уже запущен на порту 6379"
else
    echo "🚀 Запускаем Redis сервер..."
    
    # Пробуем запустить KeyDB
    bash tools/keydb_install.sh
    
    if [[ -x tools/keydb/bin/keydb-server ]]; then
        echo "📦 Запускаем KeyDB..."
        tools/keydb/bin/keydb-server --daemonize yes \
          --save "" --appendonly no \
          --bind 0.0.0.0 --port 6379 \
          --protected-mode no &
        echo "✅ KeyDB daemon started."
    else
        echo "📦 KeyDB не найден, запускаем Python fallback..."
        python3 -c "
import socket, threading, time, signal, sys

data_store = {}
shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    shutdown_flag = True
    print('\\n🛑 Stopping Redis fallback...')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def handle_client(client):
    global shutdown_flag
    while not shutdown_flag:
        try:
            client.settimeout(1.0)
            msg = client.recv(1024).decode('utf-8').strip()
            if not msg: 
                break
            
            if msg == 'PING':
                client.send(b'+PONG\\r\\n')
            elif msg.startswith('SET '):
                parts = msg.split(' ', 2)
                if len(parts) >= 3:
                    data_store[parts[1]] = parts[2]
                    client.send(b'+OK\\r\\n')
                else:
                    client.send(b'-ERR wrong number of arguments\\r\\n')
            elif msg.startswith('SETEX '):
                parts = msg.split(' ', 3)
                if len(parts) >= 4:
                    data_store[parts[1]] = parts[3]  # Игнорируем TTL для простоты
                    client.send(b'+OK\\r\\n')
                else:
                    client.send(b'-ERR wrong number of arguments\\r\\n')
            elif msg.startswith('GET '):
                key = msg.split(' ', 1)[1] if len(msg.split(' ')) > 1 else ''
                value = data_store.get(key, '')
                if value:
                    client.send(f'${len(value)}\\r\\n{value}\\r\\n'.encode())
                else:
                    client.send(b'$-1\\r\\n')
            else:
                client.send(b'-ERR unknown command\\r\\n')
        except socket.timeout:
            continue
        except:
            break
    try:
        client.close()
    except:
        pass

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 6379))
    server.listen(5)
    server.settimeout(1.0)
    print('✅ Python Redis fallback running on 0.0.0.0:6379')
    
    while not shutdown_flag:
        try:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client,), daemon=True).start()
        except socket.timeout:
            continue
        except:
            break
            
except Exception as e:
    print(f'❌ Failed to start Redis fallback: {e}')
finally:
    try:
        server.close()
    except:
        pass
" &
        echo "✅ Python Redis fallback started."
    fi
    
    # Даем время на запуск и проверяем
    sleep 3
    if netstat -tuln 2>/dev/null | grep -q ":6379 "; then
        echo "✅ Redis сервер успешно запущен"
    else
        echo "❌ Не удалось запустить Redis сервер"
    fi
fi

echo "🔍 Тестируем Redis подключение..."
python3 -c "
import redis
try:
    r = redis.Redis(host='0.0.0.0', port=6379, decode_responses=True, socket_timeout=5)
    print('🔄 Connecting to Redis...')
    result = r.ping()
    print(f'✅ Redis PING: {result}')
    r.setex('test_key', 60, 'hello')
    value = r.get('test_key')
    print(f'✅ Redis SET/GET: {value}')
except Exception as e:
    print(f'❌ Redis test failed: {e}')
"

echo "🤖 Запускаем Telegram бота..."
python daily_plan_bot.py
