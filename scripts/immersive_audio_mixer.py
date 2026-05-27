"""
Immersive Audio Mixer
Создает "живой" звук: будто пианино играет в соседней комнате,
а ты сидишь у камина и слышишь дождь за окном.

Layered audio architecture:
- Layer 1: Piano (основной, но приглушенный, как из-за стены)
- Layer 2: Room ambience (шум комнаты, скрип полов)
- Layer 3: Fireplace (тихое потрескивание)
- Layer 4: Rain / Wind (за окном, очень тихо)
- Layer 5: Occasional sounds (стук двери, шаги вдалеке)

Каждый слой имеет:
- Свою громкость (volume)
- Панораму (stereo position)
- Эффекты (reverb, low-pass filter для "за стеной")
- Рандомные появления (не все слои постоянны)
"""
import os
import random
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ImmersiveAudioMixer:
    """Микшер многослойного immersive аудио"""

    # Стандартные "рецепты" атмосфер
    RECIPES = {
        'cozy_study': {
            'description': 'Уютная комната, пианино за стеной, камин, дождь',
            'layers': {
                'piano': {'volume': 0.6, 'reverb': 0.7, 'lowpass': 3000, 'pan': 'center'},
                'fireplace': {'volume': 0.25, 'reverb': 0.3, 'lowpass': 8000, 'pan': 'left'},
                'room_ambience': {'volume': 0.15, 'reverb': 0.2, 'lowpass': 6000, 'pan': 'center'},
                'rain_window': {'volume': 0.2, 'reverb': 0.5, 'lowpass': 4000, 'pan': 'right'},
            }
        },
        'library_at_3am': {
            'description': 'Библиотека ночью, далекое пианино, тишина',
            'layers': {
                'piano': {'volume': 0.35, 'reverb': 0.9, 'lowpass': 2500, 'pan': 'center'},
                'room_ambience': {'volume': 0.1, 'reverb': 0.4, 'lowpass': 5000, 'pan': 'center'},
                'page_turns': {'volume': 0.08, 'reverb': 0.3, 'lowpass': 8000, 'pan': 'random'},
                'clock_ticking': {'volume': 0.12, 'reverb': 0.2, 'lowpass': 6000, 'pan': 'left'},
            }
        },
        'parisian_apartment': {
            'description': 'Парижская квартира, пианино соседа, город за окном',
            'layers': {
                'piano': {'volume': 0.5, 'reverb': 0.6, 'lowpass': 3500, 'pan': 'center'},
                'city_rain': {'volume': 0.3, 'reverb': 0.4, 'lowpass': 3500, 'pan': 'right'},
                'room_ambience': {'volume': 0.12, 'reverb': 0.2, 'lowpass': 6000, 'pan': 'center'},
                'distant_traffic': {'volume': 0.08, 'reverb': 0.6, 'lowpass': 2000, 'pan': 'left'},
            }
        },
        'english_manor': {
            'description': 'Английский поместье, камин, пианино в зале, ветер',
            'layers': {
                'piano': {'volume': 0.45, 'reverb': 0.8, 'lowpass': 2800, 'pan': 'center'},
                'fireplace': {'volume': 0.3, 'reverb': 0.3, 'lowpass': 7000, 'pan': 'right'},
                'wind_outside': {'volume': 0.2, 'reverb': 0.5, 'lowpass': 3000, 'pan': 'left'},
                'wood_creaks': {'volume': 0.1, 'reverb': 0.4, 'lowpass': 5000, 'pan': 'random'},
            }
        },
        'vienna_cafe': {
            'description': 'Венское кафе, фортепиано в углу, разговоры вдали',
            'layers': {
                'piano': {'volume': 0.55, 'reverb': 0.5, 'lowpass': 4000, 'pan': 'center'},
                'murmur': {'volume': 0.15, 'reverb': 0.6, 'lowpass': 2500, 'pan': 'wide'},
                'cup_clinks': {'volume': 0.08, 'reverb': 0.3, 'lowpass': 8000, 'pan': 'random'},
                'rain': {'volume': 0.18, 'reverb': 0.4, 'lowpass': 4000, 'pan': 'right'},
            }
        }
    }

    def __init__(self, sfx_library_path='../libraries/audio/sfx'):
        self.sfx_library = Path(sfx_library_path)
        self.sfx_library.mkdir(parents=True, exist_ok=True)

        # Сканируем доступные SFX
        self.available_sfx = self._scan_sfx()

    def _scan_sfx(self):
        """Сканирует библиотеку звуковых эффектов"""
        sfx = {}
        categories = ['fireplace', 'rain', 'room_ambience', 'wind', 'clock', 
                      'page_turns', 'wood_creaks', 'city_rain', 'distant_traffic',
                      'murmur', 'cup_clinks']

        for cat in categories:
            cat_path = self.sfx_library / cat
            if cat_path.exists():
                files = list(cat_path.glob('*.mp3')) + list(cat_path.glob('*.wav'))
                sfx[cat] = files

        return sfx

    def _get_pan_value(self, pan_spec):
        """Преобразует панораму в число"""
        if pan_spec == 'center':
            return 0
        elif pan_spec == 'left':
            return random.uniform(-0.7, -0.3)
        elif pan_spec == 'right':
            return random.uniform(0.3, 0.7)
        elif pan_spec == 'wide':
            return random.uniform(-0.5, 0.5)
        elif pan_spec == 'random':
            return random.uniform(-0.6, 0.6)
        return 0

    def _build_ffmpeg_filter(self, input_files, recipe_name, duration_hours):
        """Строит сложный FFmpeg filtergraph для микширования"""
        recipe = self.RECIPES[recipe_name]
        layers = recipe['layers']

        filter_parts = []
        inputs = []

        # Для каждого слоя создаем фильтр
        for i, (layer_name, params) in enumerate(layers.items()):
            if layer_name == 'piano':
                # Piano — основной трек, уже будет входом 0
                continue

            # SFX файлы
            sfx_files = self.available_sfx.get(layer_name, [])
            if not sfx_files:
                continue

            # Выбираем случайный SFX файл
            sfx_file = random.choice(sfx_files)
            inputs.append(f"-i {sfx_file}")

        # Строим filter_complex
        # Piano (input 0) + SFX (inputs 1+)
        # Каждый SFX: loop → volume → lowpass → reverb → pan

        filter_complex = ""

        # Piano track processing (input 0)
        piano_params = layers['piano']
        piano_vol = piano_params['volume']
        piano_lp = piano_params['lowpass']
        piano_pan = self._get_pan_value(piano_params['pan'])

        filter_complex += f"[0:a]aloop=loop=-1:size=2e+09,afade=t=in:ss=0:d=5,afade=t=out:st={duration_hours*3600-5}:d=5,"
        filter_complex += f"lowpass=f={piano_lp},volume={piano_vol},"
        filter_complex += f"pan=stereo|c0={0.5 + piano_pan/2}|c1={0.5 - piano_pan/2}[piano];"

        # SFX tracks
        current_input = 1
        mix_inputs = ["[piano]"]

        for layer_name, params in layers.items():
            if layer_name == 'piano':
                continue

            sfx_files = self.available_sfx.get(layer_name, [])
            if not sfx_files:
                continue

            vol = params['volume']
            lp = params['lowpass']
            pan = self._get_pan_value(params['pan'])

            # Loop SFX, apply effects
            filter_complex += f"[{current_input}:a]aloop=loop=-1:size=2e+09,"
            filter_complex += f"lowpass=f={lp},volume={vol},"
            filter_complex += f"pan=stereo|c0={0.5 + pan/2}|c1={0.5 - pan/2}[{layer_name}];"

            mix_inputs.append(f"[{layer_name}]")
            current_input += 1

        # Mix all together
        num_inputs = len(mix_inputs)
        filter_complex += f"{''.join(mix_inputs)}amix=inputs={num_inputs}:duration=longest,"
        filter_complex += f"loudnorm=I=-16:TP=-1.5:LRA=11[out]"

        return filter_complex, inputs, current_input - 1

    def create_immersive_audio(self, piano_file, recipe_name, duration_hours, output_path):
        """
        Создает immersive аудио из piano + SFX layers

        Args:
            piano_file: путь к piano треку
            recipe_name: название рецепта атмосферы
            duration_hours: длительность
            output_path: куда сохранить
        """
        if recipe_name not in self.RECIPES:
            raise ValueError(f"Неизвестный рецепт: {recipe_name}. Доступны: {list(self.RECIPES.keys())}")

        logger.info(f"🎧 Создание immersive аудио: {recipe_name} ({duration_hours}h)")
        logger.info(f"   Описание: {self.RECIPES[recipe_name]['description']}")

        filter_complex, extra_inputs, num_sfx = self._build_ffmpeg_filter(
            [piano_file], recipe_name, duration_hours
        )

        # Собираем команду FFmpeg
        cmd = ['ffmpeg', '-y', '-i', str(piano_file)]

        # Добавляем SFX inputs
        for extra in extra_inputs:
            cmd.extend(extra.split())

        cmd.extend([
            '-filter_complex', filter_complex,
            '-map', '[out]',
            '-t', str(duration_hours * 3600),
            '-c:a', 'libmp3lame', '-b:a', '192k',
            str(output_path)
        ])

        logger.info(f"   Микширую {num_sfx + 1} слоёв...")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr[:500]}")
            raise RuntimeError("Immersive audio mixing failed")

        logger.info(f"✅ Immersive аудио создано: {output_path}")
        return output_path

    def get_random_recipe(self):
        """Возвращает случайный рецепт"""
        return random.choice(list(self.RECIPES.keys()))


def main():
    """CLI тест микшера"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--piano', required=True, help='Путь к piano треку')
    parser.add_argument('--recipe', default='cozy_study', help='Рецепт атмосферы')
    parser.add_argument('--duration', type=float, default=2, help='Длительность в часах')
    parser.add_argument('--output', default='../output/immersive_audio.mp3', help='Выходной файл')

    args = parser.parse_args()

    mixer = ImmersiveAudioMixer()

    print(f"\n🎧 Доступные рецепты:")
    for name, recipe in mixer.RECIPES.items():
        print(f"  • {name}: {recipe['description']}")

    print(f"\n🎵 Создаю: {args.recipe} ({args.duration}h)...")
    mixer.create_immersive_audio(args.piano, args.recipe, args.duration, args.output)

    print(f"\n✅ Готово: {args.output}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
