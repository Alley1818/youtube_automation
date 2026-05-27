"""
Visual Generator
Решает проблему нехватки визуала
"""
import os
import io
import random
import logging
import requests
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

logger = logging.getLogger(__name__)

class AIVisualGenerator:
    """Генерация визуала через бесплатные AI API"""

    PROMPTS = {
        'cozy_fireplace': [
            "dark academia room, fireplace with warm glow, old bookshelves, candlelight, vintage aesthetic, sepia tones, 4k, cinematic",
            "old money living room, roaring fireplace, leather armchair, rain outside window, warm ambient light, photorealistic",
        ],
        'rainy_window': [
            "rain on window, cozy room inside, blurred city lights outside, dark academia aesthetic, warm interior, melancholic atmosphere",
            "vintage room with large window, heavy rain outside, candle on windowsill, dark moody lighting, cinematic",
        ],
        'library_night': [
            "oxford library at night, tall bookshelves, ladder, single desk lamp, dust particles in light beam, dark academia",
            "old library, mahogany shelves, leather books, candlelight reading nook, vintage aesthetic, 4k",
        ],
        'piano_room': [
            "vintage piano in empty room, moonlight through window, sheet music scattered, dust motes, melancholic atmosphere",
            "old grand piano, candlelight, velvet curtains, wooden floor, classical music room aesthetic",
        ],
        'parisian_apartment': [
            "parisian apartment interior, balcony doors open, rain outside, warm lamp light, vintage furniture, cozy",
            "french apartment, large windows, eiffel tower in distance, evening light, books and coffee, aesthetic",
        ],
        'english_manor': [
            "english country house interior, large fireplace, oil paintings, antique furniture, storm outside",
            "victorian drawing room, bay window, rain outside, tea set, warm lighting, dark academia aesthetic",
        ]
    }

    def __init__(self, output_dir='../libraries/visual/generated'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_with_pollinations(self, prompt, width=1920, height=1080, seed=None):
        seed = seed or random.randint(1, 999999)
        encoded_prompt = requests.utils.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
        params = {
            'width': width,
            'height': height,
            'seed': seed,
            'nologo': 'true',
            'enhance': 'true'
        }

        try:
            logger.info(f"🎨 Генерация: {prompt[:60]}...")
            response = requests.get(url, params=params, timeout=60)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                return img
            else:
                logger.warning(f"Pollinations error: {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"Pollinations failed: {e}")
            return None

    def generate_with_huggingface(self, prompt, model="stabilityai/stable-diffusion-xl-base-1.0"):
        api_token = os.getenv('HF_TOKEN', '')
        if not api_token:
            return None

        api_url = f"https://api-inference.huggingface.co/models/{model}"
        headers = {"Authorization": f"Bearer {api_token}"}

        payload = {
            "inputs": prompt,
            "parameters": {
                "width": 1920,
                "height": 1080,
                "seed": random.randint(1, 999999)
            }
        }

        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                return img
        except:
            pass
        return None

    def generate_scene(self, scene_type, save_path=None):
        if scene_type not in self.PROMPTS:
            scene_type = random.choice(list(self.PROMPTS.keys()))

        prompt = random.choice(self.PROMPTS[scene_type])
        img = self.generate_with_pollinations(prompt)

        if img is None:
            img = self.generate_with_huggingface(prompt)

        if img is None:
            logger.error("Все AI API недоступны")
            return None

        img = self._apply_vintage_effect(img)

        if save_path is None:
            timestamp = random.randint(10000, 99999)
            save_path = self.output_dir / f"{scene_type}_{timestamp}.jpg"

        img.save(save_path, quality=95)
        logger.info(f"✅ Сцена сохранена: {save_path}")
        return save_path

    def _apply_vintage_effect(self, img):
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.3)
        r, g, b = img.split()
        r = r.point(lambda i: min(255, int(i * 1.1)))
        b = b.point(lambda i: int(i * 0.85))
        img = Image.merge('RGB', (r, g, b))
        img = self._add_soft_vignette(img)
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        return img

    def _add_soft_vignette(self, img):
        width, height = img.size
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)

        for i in range(min(width, height) // 2, 0, -5):
            alpha = int(255 * (i / (min(width, height) // 2)) ** 0.7)
            draw.ellipse(
                [(width//2 - i, height//2 - i),
                 (width//2 + i, height//2 + i)],
                fill=alpha
            )

        mask = mask.filter(ImageFilter.GaussianBlur(radius=100))
        dark = Image.new('RGB', img.size, (20, 15, 30))
        img = Image.composite(img, dark, mask)
        return img

    def generate_batch(self, scene_types=None, count=10):
        scene_types = scene_types or list(self.PROMPTS.keys())
        generated = []

        for i in range(count):
            scene = random.choice(scene_types)
            path = self.generate_scene(scene)
            if path:
                generated.append(path)

        logger.info(f"✅ Сгенерировано {len(generated)} сцен")
        return generated


class ProceduralVisualGenerator:
    def __init__(self, output_dir='../libraries/visual/procedural'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_candle_scene(self, width=1920, height=1080):
        img = Image.new('RGB', (width, height), (10, 8, 15))
        draw = ImageDraw.Draw(img)

        for y in range(height):
            darkness = int(10 + (y / height) * 20)
            draw.line([(0, y), (width, y)], fill=(darkness, darkness - 2, darkness + 5))

        num_candles = random.randint(3, 7)
        for _ in range(num_candles):
            x = random.randint(200, width - 200)
            y = random.randint(height // 2, height - 100)
            candle_h = random.randint(80, 150)
            draw.rectangle([x - 8, y - candle_h, x + 8, y], fill=(240, 230, 200))

            flame_colors = [(255, 200, 50), (255, 150, 30), (255, 100, 20)]
            for i, color in enumerate(flame_colors):
                offset = i * 3
                draw.ellipse([x - 12 + offset, y - candle_h - 25 + offset,
                             x + 12 - offset, y - candle_h + 5 - offset], fill=color)

            for r in range(80, 10, -10):
                alpha = int(20 * (r / 80))
                draw.ellipse([x - r, y - candle_h - r, x + r, y - candle_h + r],
                           fill=(255, 200, 100, alpha))

        pixels = img.load()
        for i in range(0, width, 3):
            for j in range(0, height, 3):
                r, g, b = pixels[i, j]
                noise = random.randint(-8, 8)
                pixels[i, j] = (
                    max(0, min(255, r + noise)),
                    max(0, min(255, g + noise)),
                    max(0, min(255, b + noise))
                )

        return img

    def generate_window_rain(self, width=1920, height=1080):
        img = Image.new('RGB', (width, height), (15, 15, 25))
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, width, height], fill=(20, 18, 25))

        win_x, win_y = 400, 150
        win_w, win_h = 800, 500

        draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(5, 8, 20))

        for _ in range(200):
            rx = random.randint(win_x, win_x + win_w)
            ry = random.randint(win_y, win_y + win_h)
            draw.line([(rx, ry), (rx + random.randint(-5, 5), ry + random.randint(20, 40))],
                     fill=(100, 110, 130), width=1)

        draw.rectangle([win_x - 10, win_y - 10, win_x + win_w + 10, win_y + win_h + 10],
                      outline=(60, 50, 40), width=15)
        draw.line([(win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h)],
                 fill=(60, 50, 40), width=10)
        draw.line([(win_x, win_y + win_h // 2), (win_x + win_w, win_y + win_h // 2)],
                 fill=(60, 50, 40), width=10)

        draw.rectangle([win_x - 20, win_y + win_h + 10, win_x + win_w + 20, win_y + win_h + 40],
                      fill=(50, 40, 30))

        cx, cy = win_x + 100, win_y + win_h + 5
        draw.rectangle([cx - 6, cy - 40, cx + 6, cy], fill=(240, 230, 200))
        draw.ellipse([cx - 10, cy - 55, cx + 10, cy - 35], fill=(255, 200, 50))

        for r in range(100, 0, -5):
            alpha = int(15 * (r / 100))
            draw.ellipse([cx - r, cy - 60 - r, cx + r, cy - 60 + r],
                       fill=(255, 180, 80, alpha))

        return img

    def generate_and_save(self, scene_type='candle', count=5):
        generators = {
            'candle': self.generate_candle_scene,
            'window_rain': self.generate_window_rain,
        }

        gen_func = generators.get(scene_type, self.generate_candle_scene)
        saved = []

        for i in range(count):
            img = gen_func()
            path = self.output_dir / f"{scene_type}_{i:03d}.jpg"
            img.save(path, quality=95)
            saved.append(path)

        return saved


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', default='ai', choices=['ai', 'procedural', 'both'])
    parser.add_argument('--scene', default='cozy_fireplace')
    parser.add_argument('--count', type=int, default=5)
    parser.add_argument('--output', default='../libraries/visual/generated')
    args = parser.parse_args()

    if args.method in ['ai', 'both']:
        print("🎨 Генерация через AI...")
        ai_gen = AIVisualGenerator(args.output)
        ai_gen.generate_batch(count=args.count)

    if args.method in ['procedural', 'both']:
        print("🔧 Процедурная генерация...")
        proc_gen = ProceduralVisualGenerator(args.output + "_procedural")
        proc_gen.generate_and_save('candle', args.count)
        proc_gen.generate_and_save('window_rain', args.count)

    print(f"\n✅ Готово! Проверь: {args.output}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()