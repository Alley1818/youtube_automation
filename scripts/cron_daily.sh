#!/bin/bash
# cron_daily.sh — ежедневный автоматический запуск
# Добавить в crontab: 0 10 * * * /path/to/cron_daily.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/../logs/cron_$(date +%Y%m%d).log"

echo "$(date): Начало ежедневного создания" >> "$LOG_FILE"

# Создаём 1 видео в день
python "$SCRIPT_DIR/create_video.py" --auto >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "$(date): ✅ Видео создано и залито" >> "$LOG_FILE"
else
    echo "$(date): ❌ Ошибка создания видео" >> "$LOG_FILE"
fi
