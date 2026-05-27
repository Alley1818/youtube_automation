# Classical Piano Automation Agent
## Стиль Dear Victor and Victoria (Old Money / Dark Academia)

Полностью автоматизированный агент для создания и заливки classical piano видео на YouTube.

---

## 🎯 Что делает агент

1. **Выбирает** случайный трек из библиотеки public domain classical music
2. **Выбирает** случайный визуал (vintage интерьеры, свечи, дождь за окном, библиотеки)
3. **Склеивает** 2-3 часовое видео через FFmpeg
4. **Генерирует** thumbnail в стиле Dark Academia (sepia, винтажные шрифты)
5. **Создаёт** SEO-оптимизированное название, описание, теги
6. **Заливает** на YouTube через Data API v3
7. **Логирует** всё

---

## 📁 Структура

```
classical_piano_automation/
├── config/
│   ├── settings.yaml              # Настройки канала
│   └── youtube_credentials.json   # Google API credentials (ты создаёшь)
├── scripts/
│   ├── create_video.py            # Главный оркестратор
│   ├── audio_processor.py         # Обработка аудио (loop, fade, normalize)
│   ├── visual_processor.py        # Подготовка визуала
│   ├── thumbnail_generator.py     # Генерация превью (PIL)
│   └── youtube_uploader.py        # Заливка через API
├── templates/
│   ├── titles.json                # Шаблоны названий (old money стиль)
│   ├── descriptions.json          # Шаблоны описаний
│   └── tags.json                  # Теги по нишам
├── libraries/
│   ├── audio/classical/           # .mp3 файлы (Musopen, public domain)
│   └── visual/
│       ├── vintage/               # .mp4/.jpg (Pixabay: candles, libraries, piano)
│       └── nature/                # .mp4/.jpg (Pixabay: rain window, forest)
├── output/                        # Готовые видео
└── logs/                          # Логи операций
```

---

## 🚀 Быстрый старт

### Шаг 1: Установка зависимостей

```bash
pip install -r requirements.txt
```

Также нужно установить **FFmpeg**:
- **Windows**: `choco install ffmpeg` или скачать с [ffmpeg.org](https://ffmpeg.org)
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

### Шаг 2: Собрать библиотеку

**Аудио (public domain classical):**
1. Идёшь на [Musopen.org](https://musopen.org)
2. Скачиваешь: Chopin Nocturnes, Debussy Clair de Lune, Bach Goldberg Variations, Mozart Piano Sonatas
3. Кладёшь в `libraries/audio/classical/`

**Визуал (vintage / dark academia):**
1. Идёшь на [Pixabay.com/videos](https://pixabay.com/videos)
2. Ищешь: "vintage library", "candle light", "rain window", "old piano", "dark academia room"
3. Скачиваешь 20-30 видео
4. Кладёшь в `libraries/visual/vintage/` и `libraries/visual/nature/`

### Шаг 3: Настроить YouTube API

1. [Google Cloud Console](https://console.cloud.google.com) → New Project
2. APIs & Services → Enable **YouTube Data API v3**
3. OAuth consent screen → External → заполняешь данные
4. Credentials → Create OAuth client ID → Desktop app
5. Скачиваешь `client_secret.json` → кладёшь в `config/`
6. Переименовываешь в `youtube_credentials.json`

### Шаг 4: Первый запуск

```bash
cd scripts
python create_video.py --niche classical --duration 2 --mood melancholic --activity study
```

При первом запуске откроется браузер — авторизуй Google аккаунт канала.
Токен сохранится автоматически.

---

## 🎨 Стиль Dear Victor and Victoria

### Названия (examples)
- "a playlist for those born in the wrong century • chopin nocturnes"
- "old money vibes | debussy for dark academia studying"
- "royal is falling in love with you • classical piano 2 hours"
- "slow living in a parisian apartment | rain + chopin"
- "you come from old money, but it's 1948 | classical study"

### Визуал
- Sepia / warm tones
- Свечи, старые книги, окна с дождём
- Винтажные интерьеры, пианино
- Медленный zoom/pan (Ken Burns effect)

### Thumbnail
- Тёмный фон, золотистый текст
- Шрифты: serif (Times, Garamond)
- Элементы: свечи, перья, старые карты

---

## 📊 Масштабирование

```bash
# Запуск через cron (Linux/Mac) или Task Scheduler (Windows)
# Каждый день в 10:00
0 10 * * * cd /path/to/scripts && python create_video.py --auto
```

**Один человек, 20 каналов:**
- Настройка: 40 часов
- Ежедневно: 1 команда = 1 видео
- 20 каналов × 7 видео/нед = 140 видео/неделю

---

## ⚠️ Важно

- **Public domain**: только композиторы, умершие >70 лет назад (Chopin, Bach, Mozart, Debussy — умер в 1918, Chopin в 1849)
- **Записи**: убедись, что записи тоже public domain (Musopen гарантирует это)
- **Квота API**: 6 видео/день на стандартной квоте. Для больше — запрашивай увеличение

---

## 💰 Монетизация

- **AdSense**: 100% дохода (нет Content ID на public domain)
- **RPM**: $5-12 (classical ниша, аудитория USA/Europe)
- **Доход 1 канала за 2 года**: $12,000+ (оптимистично)
- **20 каналов**: $240,000+
