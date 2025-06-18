#!/usr/bin/env bash
set -e
if [[ ! -d tools/keydb/bin ]]; then
    echo "🔄  Downloading KeyDB binary..."
    curl -L -o keydb.tar.gz \
      "https://github.com/Snapchat/KeyDB/releases/download/v6.3.4/keydb-6.3.4-x86_64.tar.gz"
    mkdir -p tools/keydb && tar -xzf keydb.tar.gz -C tools/keydb --strip-components=1
    rm keydb.tar.gz
    echo "✅  KeyDB installed."
fi