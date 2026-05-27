"""
Create Video — Главный оркестратор v2.0
"""
import os
import sys
import json
import random
import logging
import argparse
from pathlib import Path
from datetime import datetime

# Определяем корень проекта
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

sys.path.insert(0, str(SCRIPT_DIR))

from audio_processor import AudioProcessor
from visual_processor import VisualProcessor
from thumbnail_generator import ThumbnailGenerator
from youtube_uploader import YouTubeUploader
from ai_title_generator import AITitleGenerator
from immersive_audio_mixer import ImmersiveAudioMixer
from visual_generator import AIVisualGenerator, ProceduralVisualGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(str(PROJECT_ROOT / 'logs' / f'automation_{datetime.now().strftime("%Y%m%d")}.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VideoCreatorV2:
    def __init__(self, config_path=None):
        self.base_dir = PROJECT_ROOT

        # Если путь не указан — используем стандартный
        if config_path is None:
            config_path = self.base_dir / 'config' / 'settings.yaml'
        else:
            config_path = Path(config_path)

        self.config = self._load_config(config_path)

        # Компоненты с абсолютными путями
        self.audio_processor = AudioProcessor(self.base_dir / 'libraries' / 'audio' / 'classical')
        self.visual_processor = VisualProcessor(self.base_dir / 'libraries' / 'visual')
        self.thumbnail_generator = ThumbnailGenerator(self.base_dir / 'templates')
        self.ai_title_gen = AITitleGenerator(api_provider='gemini')
        self.immersive_mixer = ImmersiveAudioMixer(self.base_dir / 'libraries' / 'audio' / 'sfx')
        self.visual_generator = AIVisualGenerator(self.base_dir / 'libraries' / 'visual' / 'generated')
        self.proc_visual = ProceduralVisualGenerator(self.base_dir / 'libraries' / 'visual' / 'procedural')

        self.youtube_uploader = None

    def _load_config(self, config_path):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def generate_metadata(self, composer, mood, activity, duration, use_ai=True):
        if use_ai:
            title = self.ai_title_gen.generate(composer, mood, activity, duration)
        else:
            title = self.ai_title_gen.fallback_generator.generate(composer, mood, activity, duration)

        descriptions = {
            'templates': [
                f"{title}\n\nthis is my personal love letter to {composer}.\n\na {mood} atmosphere for {activity}. {duration} hours. no ads. no interruptions.\n\n#classicalmusic #darkacademia #{composer} #piano",
                f"{title}\n\nfor those who find comfort in the past.\n\n{composer} playing in the next room, while you {activity}.\n\n{duration} hours of uninterrupted beauty.\n\n#classicalpiano #{composer} #darkacademia #oldmoney",
            ]
        }
        description = random.choice(descriptions['templates'])

        tags = [
            composer, mood, activity, f"{duration} hours",
            "classical music", "piano", "dark academia", "old money",
            "study music", "focus music", "ambient", "no ads"
        ]

        return {
            'title': title,
            'description': description,
            'tags': tags,
            'composer': composer,
            'mood': mood,
            'duration': duration
        }

    def create_video(self, niche='classical', duration=2, mood='melancholic',
                     activity='studying', composer=None, use_ai_titles=True,
                     use_immersive=True, auto_upload=True):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = self.base_dir / 'output'
        output_dir.mkdir(exist_ok=True)

        logger.info(f"🎬 Создание видео: {niche} | {duration}h | {mood} | immersive={use_immersive}")

        # 1. Метаданные
        metadata = self.generate_metadata(composer or 'chopin', mood, activity, duration, use_ai_titles)
        logger.info(f"📝 Title: {metadata['title']}")

        # 2. Аудио
        audio_files = self.audio_processor.get_random_audio(count=1)

        if use_immersive and self.immersive_mixer.available_sfx:
            logger.info("🎧 Создание immersive аудио...")
            recipe = self.immersive_mixer.get_random_recipe()
            audio_output = output_dir / f"audio_immersive_{timestamp}.mp3"
            self.immersive_mixer.create_immersive_audio(
                audio_files[0], recipe, duration, audio_output
            )
        else:
            logger.info("🎵 Создание обычного аудио...")
            audio_output = output_dir / f"audio_{timestamp}.mp3"
            self.audio_processor.create_long_audio(
                audio_files, duration, audio_output,
                fade_in=5, fade_out=5
            )

        # 3. Визуал
        try:
            visual_file = self.visual_processor.get_random_visual(style='vintage')
            logger.info(f"🎨 Использован существующий визуал: {visual_file.name}")
        except:
            logger.info("🎨 Генерация нового визуала...")
            visual_path = self.visual_generator.generate_scene('cozy_fireplace')
            if visual_path is None:
                visual_path = self.proc_visual.generate_and_save('candle', 1)[0]
            visual_file = visual_path

        visual_output = output_dir / f"visual_{timestamp}.mp4"
        self.visual_processor.create_long_visual(
            Path(visual_file), duration, visual_output,
            apply_sepia=True, apply_slow_zoom=True
        )

        # 4. Склейка
        final_video = output_dir / f"{mood}_{duration}h_{timestamp}.mp4"
        import subprocess
        cmd = [
            'ffmpeg', '-y',
            '-i', str(visual_output),
            '-i', str(audio_output),
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(final_video)
        ]
        subprocess.run(cmd, capture_output=True)

        # 5. Thumbnail
        thumbnail_path = output_dir / f"thumb_{timestamp}.jpg"
        self.thumbnail_generator.generate(metadata['title'], metadata['composer'], mood, thumbnail_path)

        # 6. Заливка
        video_id = None
        if auto_upload:
            if not self.youtube_uploader:
                creds_path = self.base_dir / 'config' / 'youtube_credentials.json'
                self.youtube_uploader = YouTubeUploader(creds_path)

            video_id = self.youtube_uploader.upload_video(
                str(final_video), metadata['title'], metadata['description'],
                metadata['tags'], '10', 'public', str(thumbnail_path)
            )

        # Cleanup
        audio_output.unlink(missing_ok=True)
        visual_output.unlink(missing_ok=True)

        return {
            'metadata': metadata,
            'video_path': str(final_video),
            'video_id': video_id,
            'youtube_url': f"https://youtube.com/watch?v={video_id}" if video_id else None
        }

def main():
    parser = argparse.ArgumentParser(description='Classical Piano Video Creator v2.0')
    parser.add_argument('--niche', default='classical')
    parser.add_argument('--duration', type=float, default=2)
    parser.add_argument('--mood', default='melancholic')
    parser.add_argument('--activity', default='studying')
    parser.add_argument('--composer', default=None)
    parser.add_argument('--auto', action='store_true', help='Авто-режим')
    parser.add_argument('--immersive', action='store_true', help='Immersive audio')
    parser.add_argument('--ai-titles', action='store_true', help='AI названия')
    parser.add_argument('--no-upload', action='store_true')

    args = parser.parse_args()

    if args.auto:
        moods = ['melancholic', 'ethereal', 'nostalgic', 'dreamy', 'serene']
        activities = ['studying', 'reading', 'sleeping', 'focus', 'contemplation']
        args.mood = random.choice(moods)
        args.activity = random.choice(activities)
        args.duration = random.choice([1.5, 2, 3])
        args.immersive = True
        args.ai_titles = True

    creator = VideoCreatorV2()
    result = creator.create_video(
        niche=args.niche,
        duration=args.duration,
        mood=args.mood,
        activity=args.activity,
        composer=args.composer,
        use_ai_titles=args.ai_titles,
        use_immersive=args.immersive,
        auto_upload=not args.no_upload
    )

    print(f"\n✅ Готово!")
    print(f"🎬 {result['metadata']['title']}")
    if result['video_id']:
        print(f"🔗 {result['youtube_url']}")

if __name__ == '__main__':
    main()