"""
Thumbnail Generator
Создаёт превью в стиле Dear Victor and Victoria:
- Тёмный фон (#1a1a2e)
- Золотой текст (#d4af37)
- Винтажные шрифты
- Элементы: свечи, перья, старые карты (через overlay)
"""
import os
import random
import logging
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

class ThumbnailGenerator:
    def __init__(self, templates_dir):
        self.templates_dir = Path(templates_dir)
        self.width = 1280
        self.height = 720

        # Цвета в стиле Dear Victor and Victoria
        self.bg_color = (26, 26, 46)  # #1a1a2e — тёмно-синий
        self.text_color = (212, 175, 55)  # #d4af37 — золотой
        self.accent_color = (139, 69, 19)  # #8b4513 — коричневый
        self.subtext_color = (200, 200, 200)  # светло-серый

    def _get_font(self, size, bold=False):
        """Пытается найти винтажный serif шрифт"""
        font_paths = [
            "/usr/share/fonts/truetype/times.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
            "/System/Library/Fonts/Times.ttc",  # Mac
            "C:/Windows/Fonts/times.ttf",  # Windows
            "C:/Windows/Fonts/georgia.ttf",
        ]

        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue

        return ImageFont.load_default()

    def generate(self, title, composer, mood, output_path):
        """
        Генерирует thumbnail

        Args:
            title: название видео
            composer: имя композитора
            mood: настроение
            output_path: куда сохранить
        """
        # Создаём базовое изображение
        img = Image.new('RGB', (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)

        # Добавляем текстурный эффект (шум/градиент для винтажности)
        self._add_texture(img)

        # Добавляем декоративные элементы
        self._add_decorations(draw)

        # Главный текст
        main_font = self._get_font(48, bold=True)

        # Разбиваем title на строки если слишком длинный
        lines = self._wrap_text(title, main_font, self.width - 100)

        y_start = 200
        line_height = 60

        for i, line in enumerate(lines):
            # Тень для depth
            draw.text((51, y_start + i * line_height + 1), line, 
                     fill=(0, 0, 0), font=main_font)
            # Основной текст
            draw.text((50, y_start + i * line_height), line, 
                     fill=self.text_color, font=main_font)

        # Подпись композитора
        composer_font = self._get_font(32)
        composer_text = f"~ {composer.upper()} ~"
        draw.text((50, y_start + len(lines) * line_height + 30), 
                 composer_text, fill=self.subtext_color, font=composer_font)

        # Mood tag
        mood_font = self._get_font(24)
        mood_text = f"{mood} • classical piano"
        draw.text((50, self.height - 100), mood_text, 
                 fill=self.accent_color, font=mood_font)

        # Добавляем виньетку (затемнение по краям)
        img = self._add_vignette(img)

        # Сохраняем
        img.save(output_path, quality=95)
        logger.info(f"Thumbnail создан: {output_path}")
        return output_path

    def _add_texture(self, img):
        """Добавляет текстуру старой бумаги/пергамента"""
        # Создаём лёгкий шум
        pixels = img.load()
        for i in range(0, self.width, 4):
            for j in range(0, self.height, 4):
                r, g, b = pixels[i, j]
                noise = random.randint(-10, 10)
                pixels[i, j] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )

    def _add_decorations(self, draw):
        """Добавляет декоративные линии и элементы"""
        # Верхняя линия
        draw.line([(50, 50), (self.width - 50, 50)], 
                 fill=self.accent_color, width=2)

        # Нижняя линия
        draw.line([(50, self.height - 50), (self.width - 50, self.height - 50)], 
                 fill=self.accent_color, width=2)

        # Угловые элементы (ромбы)
        for x, y in [(40, 40), (self.width - 60, 40), 
                     (40, self.height - 60), (self.width - 60, self.height - 60)]:
            draw.polygon([(x, y), (x+10, y+5), (x, y+10), (x-10, y+5)], 
                      fill=self.text_color)

    def _wrap_text(self, text, font, max_width):
        """Разбивает текст на строки по ширине"""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0] if bbox else 0

            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        return lines if lines else [text]

    def _add_vignette(self, img):
        """Добавляет виньетку (затемнение по краям)"""
        # Создаём градиентную маску
        vignette = Image.new('L', (self.width, self.height), 0)
        v_draw = ImageDraw.Draw(vignette)

        # Рисуем градиент от центра
        for i in range(min(self.width, self.height) // 2, 0, -1):
            alpha = int(255 * (1 - (i / (min(self.width, self.height) // 2)) ** 0.5))
            v_draw.ellipse(
                [(self.width//2 - i, self.height//2 - i),
                 (self.width//2 + i, self.height//2 + i)],
                fill=alpha
            )

        # Применяем виньетку
        vignette = vignette.filter(ImageFilter.GaussianBlur(radius=50))
        img = Image.composite(img, Image.new('RGB', img.size, (0, 0, 0)), vignette)
        return img
