#!/bin/bash

# Start server ở nền
/bin/ollama serve &

pid=$!

# Đợi ollama sẵn sàng
until curl -s http://localhost:11434 > /dev/null; do
  echo "🕒 Waiting for Ollama to be ready..."
  sleep 1
done

# Pull model
echo "⬇️ Pulling model: bge-m3:567m"
/bin/ollama pull bge-m3:567m

# Giữ container sống
wait $pid
