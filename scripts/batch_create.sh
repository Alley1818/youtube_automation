#!/bin/bash
# batch_create.sh — массовое создание видео
# Запуск: ./batch_create.sh 7 (создаст 7 видео)

COUNT=${1:-7}  # По умолчанию 7 видео
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🎬 Создание $COUNT видео..."
echo "================================"

for i in $(seq 1 $COUNT); do
    echo ""
    echo "[$i/$COUNT] Создание видео..."
    python "$SCRIPT_DIR/create_video.py" --auto --no-upload

    # Пауза между видео (чтобы не перегрузить API и дать FFmpeg отдохнуть)
    if [ $i -lt $COUNT ]; then
        echo "⏳ Пауза 30 секунд..."
        sleep 30
    fi
done

echo ""
echo "✅ Все $COUNT видео созданы!"
echo "Проверь папку output/ и залей через create_video.py --no-upload"
