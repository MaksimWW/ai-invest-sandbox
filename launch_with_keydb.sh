
#!/usr/bin/env bash
# 1) ensure KeyDB binary exists
bash tools/keydb_install.sh
# 2) start keydb if not running
if ! pgrep -f "keydb-server" > /dev/null; then
    if [[ -x tools/keydb/bin/keydb-server ]]; then
        tools/keydb/bin/keydb-server --daemonize yes \
          --save "" --appendonly no \
          --bind 127.0.0.1 --port 6379 &
        echo "🚀 KeyDB daemon started."
        sleep 2  # даем время на запуск
    else
        echo "❌ KeyDB server not found. Starting Python fallback..."
        python3 -c "
import socket, threading, time
data_store = {}

def handle_client(client):
    while True:
        try:
            msg = client.recv(1024).decode('utf-8').strip()
            if not msg: break
            
            if msg == 'PING':
                client.send(b'+PONG\r\n')
            elif msg.startswith('SET '):
                parts = msg.split(' ', 2)
                if len(parts) >= 3:
                    data_store[parts[1]] = parts[2]
                    client.send(b'+OK\r\n')
            elif msg.startswith('GET '):
                key = msg.split(' ', 1)[1]
                value = data_store.get(key, '')
                if value:
                    client.send(f'${len(value)}\r\n{value}\r\n'.encode())
                else:
                    client.send(b'$-1\r\n')
        except:
            break
    client.close()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 6379))
server.listen(5)
print('Simple Redis running on port 6379')

while True:
    client, addr = server.accept()
    threading.Thread(target=handle_client, args=(client,)).start()
" &
        echo "🚀 Python Redis fallback started."
    fi
fi
# 3) start the original repl command
python daily_plan_bot.py
