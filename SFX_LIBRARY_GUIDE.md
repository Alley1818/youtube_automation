# 🎧 SFX Library Guide
## Где брать звуки для Immersive Audio Mixer

---

## Принцип микширования (как не мешать музыке)

```
Частотный спектр:
20Hz ────────────────────────────────────── 20kHz
  │     │           │              │         │
  │  SUB       LOW-MID        HIGH-MID     TREBLE
  │  (бас)    (музыка)       (дождь)    (шипение)
  │     │           │              │         │
  │     └───────────┴──────────────┘         │
  │           PIANO (основной)               │
  │                                          │
  └──── FIREPLACE (низкие гулкие) ──────────┘
       RAIN (средне-высокие шипящие)
```

**Правило:**
- Piano = 200Hz–4kHz (весь спектр, но акцент на середине)
- Fireplace = 50–500Hz (низкий гул, не пересекается с мелодией)
- Rain = 4kHz–12kHz (высокое шипение, "за окном")
- Room ambience = 100Hz–1kHz (очень тихо)

---

## Источники SFX (все бесплатные)

### 1. Freesound.org (основной)

| Звук | Поисковый запрос | Лицензия | Ссылка |
|------|-------------------|----------|--------|
| **Камин (тихий)** | "fireplace crackling gentle" | CC0 / CC-BY | [freesound.org](https://freesound.org) |
| **Камин (гулкий)** | "fireplace low rumble" | CC0 | [freesound.org](https://freesound.org) |
| **Дождь лёгкий** | "rain gentle window" | CC0 | [freesound.org](https://freesound.org) |
| **Дождь сильный** | "rain heavy outside" | CC0 | [freesound.org](https://freesound.org) |
| **Шаги по дереву** | "footsteps wood floor distant" | CC0 | [freesound.org](https://freesound.org) |
| **Скрип двери** | "door creak old" | CC0 | [freesound.org](https://freesound.org) |
| **Шум комнаты** | "room tone quiet" | CC0 | [freesound.org](https://freesound.org) |
| **Часы тикают** | "clock ticking grandfather" | CC0 | [freesound.org](https://freesound.org) |
| **Поворот страницы** | "page turn book" | CC0 | [freesound.org](https://freesound.org) |
| **Ветер** | "wind howling distant" | CC0 | [freesound.org](https://freesound.org) |
| **Город вдали** | "city ambience distant" | CC0 | [freesound.org](https://freesound.org) |
| **Разговоры (неразборчиво)** | "murmur cafe distant" | CC0 | [freesound.org](https://freesound.org) |

**Как скачивать:**
1. Регистрация бесплатная
2. Ищешь запрос
3. Фильтр: License = "Creative Commons 0" (CC0 = можно всё)
4. Скачиваешь .wav или .mp3

### 2. YouTube Audio Library (SFX раздел)

| Категория | Что найдёшь | Лицензия |
|-----------|-------------|----------|
| Ambience | Room tones, nature | Бесплатно, любое использование |
| Fire | Fireplace, sparks | Бесплатно |
| Weather | Rain, wind, thunder | Бесплатно |
| Domestic | Door creaks, footsteps | Бесплатно |

**Ссылка:** [YouTube Audio Library — Sound effects](https://www.youtube.com/audiolibrary/soundeffects)

### 3. BBC Sound Effects Library

| Что есть | Лицензия | Ссылка |
|----------|----------|--------|
| 16,000+ звуков (погода, природа, быт) | RemArc License (некоммерческое, но YouTube = ОК) | [bbcsfx.acropolis.org.uk](https://bbcsfx.acropolis.org.uk) |

### 4. ZapSplat

| Что есть | Лицензия | Ссылка |
|----------|----------|--------|
| 100,000+ SFX | Бесплатно с атрибуцией | [zapsplat.com](https://www.zapsplat.com) |

---

## Структура папок SFX

```
libraries/audio/sfx/
├── fireplace/
│   ├── gentle_crackling_01.wav      # Тихое потрескивание
│   ├── gentle_crackling_02.wav      # Альтернатива
│   ├── low_rumble.wav               # Глубокий гул
│   └── sparks_pop.wav               # Вспышки искр
│
├── rain/
│   ├── light_window_01.wav          # Лёгкий дождь за окном
│   ├── light_window_02.wav
│   ├── heavy_outside_01.wav         # Сильный дождь
│   └── roof_rain.wav                # Дождь по крыше
│
├── room_ambience/
│   ├── quiet_room_tone.wav          # Тишина комнаты
│   ├── wood_floor_creak.wav         # Скрип полов
│   └── house_settling.wav           # "Вздох" дома
│
├── footsteps/
│   ├── wood_distant_01.wav          # Шаги по дереву
│   ├── wood_distant_02.wav
│   └── stairs_creak.wav             # Скрип лестницы
│
├── clock/
│   ├── grandfather_ticking.wav      # Тиканье часов
│   └── clock_chime_distant.wav      # Удары часов
│
├── page_turns/
│   ├── page_turn_01.wav
│   ├── page_turn_02.wav
│   └── book_close.wav
│
├── wind/
│   ├── gentle_outside.wav           # Лёгкий ветер
│   ├── howling_distant.wav          # Вой вдали
│   └── window_rattle.wav            # Дребезжание окна
│
├── city/
│   ├── distant_traffic.wav          # Трафик вдали
│   ├── murmur_cafe.wav              # Гул кафе
│   └── night_crickets.wav           # Сверчки
│
└── occasional/
    ├── door_creak.wav               # Скрип двери
    ├── cup_clink.wav                # Звон чашки
    ├── thunder_distant.wav          # Гром вдали
    └── cat_meow_distant.wav         # Кошка (очень тихо)
```

---

## Технические параметры микширования

### Частотная фильтрация (EQ)

| Слой | High-Pass | Low-Pass | Почему |
|------|-----------|----------|--------|
| **Piano** | 80Hz | 8kHz | Убираем ненужный низ, оставляем тело |
| **Fireplace** | 60Hz | 600Hz | Только низкий гул, не лезет в мелодию |
| **Rain** | 3kHz | 12kHz | Только высокое шипение, "воздух" |
| **Room** | 100Hz | 2kHz | Очень узкий диапазон, фон |
| **Footsteps** | 200Hz | 4kHz | Средние частоты, но тихо |

### Панорамирование (Stereo Position)

```
        СЛУШАТЕЛЬ
            ↑
   ←──────┼──────→
   Лево   │   Право
          │
  [Камин] │ [Дождь]
     ↓    │    ↓
   Pan:   │   Pan:
   -0.4   │   +0.5
          │
    [Piano — Center]
         ↓
       Pan: 0
```

### Громкость (Volume)

| Слой | Volume | Почему |
|------|--------|--------|
| **Piano** | 60-70% | Главное, но не в лицо |
| **Fireplace** | 20-30% | Ощутимо, но не отвлекает |
| **Rain** | 15-25% | Фон, создаёт глубину |
| **Room** | 8-15% | Подсознательно |
| **Occasional** | 5-10% | Редкие всплески |

### Реверберация (Reverb / "Пространство")

| Слой | Reverb | Почему |
|------|--------|--------|
| **Piano** | 60-80% | "Из соседней комнаты" — далеко, но слышно |
| **Fireplace** | 20-40% | Близко, мало реверба |
| **Rain** | 50-70% | За окном, отражения от стекла |
| **Room** | 10-30% | Поглощается мебелью |

---

## Рецепты атмосфер (пресеты)

### "Cozy Study" (Уютная комната)
```
Piano:     vol=0.65, pan=0,    reverb=0.75, lp=3500
Fireplace: vol=0.28, pan=-0.4, reverb=0.30, lp=600
Rain:      vol=0.20, pan=+0.5, reverb=0.55, lp=4000
Room:      vol=0.12, pan=0,    reverb=0.20, lp=1500
```

### "Library at 3AM" (Библиотека ночью)
```
Piano:      vol=0.40, pan=0,    reverb=0.90, lp=2500
Room:       vol=0.08, pan=0,    reverb=0.40, lp=1200
Clock:      vol=0.12, pan=-0.3, reverb=0.20, lp=2000
Page turns: vol=0.05, pan=+0.2, reverb=0.30, lp=3000 (редко)
```

### "Parisian Apartment" (Парижская квартира)
```
Piano:    vol=0.55, pan=0,    reverb=0.60, lp=4000
Rain:     vol=0.30, pan=+0.5, reverb=0.40, lp=3500
City:     vol=0.10, pan=-0.3, reverb=0.70, lp=1800
Room:     vol=0.10, pan=0,    reverb=0.20, lp=1500
```

### "English Manor" (Английский особняк)
```
Piano:     vol=0.50, pan=0,    reverb=0.80, lp=2800
Fireplace: vol=0.35, pan=+0.4, reverb=0.25, lp=700
Wind:      vol=0.20, pan=-0.5, reverb=0.60, lp=2500
Wood:      vol=0.08, pan=0,    reverb=0.40, lp=2000 (редко)
```

### "Vienna Cafe" (Венское кафе)
```
Piano:   vol=0.60, pan=0,    reverb=0.50, lp=4500
Murmur:  vol=0.15, pan=0,    reverb=0.70, lp=2200 (wide stereo)
Rain:    vol=0.18, pan=+0.4, reverb=0.40, lp=3800
Cups:    vol=0.06, pan=-0.2, reverb=0.25, lp=5000 (очень редко)
```

---

## Чек-лист перед запуском

- [ ] Скачано 3-5 вариантов fireplace
- [ ] Скачано 3-5 вариантов rain
- [ ] Скачано 2-3 room tone
- [ ] Скачано 2-3 footsteps
- [ ] Скачано 1-2 clock ticking
- [ ] Все файлы в .wav или .mp3
- [ ] Все файлы CC0 (проверено на Freesound)
- [ ] Папки созданы по структуре выше
- [ ] Тестовый запуск immersive_audio_mixer.py прошёл
