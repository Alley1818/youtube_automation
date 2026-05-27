"""
Visual Processor — Оптимизирован для Apple Silicon M2
Использует videotoolbox (GPU ускорение)
"""
import os
import random
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class VisualProcessor:
    def __init__(self, visual_library_path):
        self.visual_library = Path(visual_library_path)
        self.visual_files = []
        self._scan_library()

    def _scan_library(self):
        extensions = ('.mp4', '.mov', '.avi', '.mkv', '.jpg', '.jpeg', '.png')
        self.visual_files = [
            f for f in self.visual_library.rglob('*')
            if f.suffix.lower() in extensions
        ]
        logger.info(f"Найдено визуальных файлов: {len(self.visual_files)}")

    def get_random_visual(self, style=None):
        if not self.visual_files:
            raise ValueError("Библиотека визуалов пуста!")

        candidates = self.visual_files
        if style:
            style_path = self.visual_library / style
            if style_path.exists():
                candidates = [f for f in candidates if style in str(f)]

        if not candidates:
            candidates = self.visual_files

        return random.choice(candidates)

    def get_video_duration(self, video_path):
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(video_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    def create_long_visual(self, visual_file, target_duration_hours, output_path,
                          apply_sepia=False, apply_slow_zoom=False):

        target_seconds = target_duration_hours * 3600
        is_image = visual_file.suffix.lower() in ('.jpg', '.jpeg', '.png')

        # GPU ускорение для M2
        encoder = 'h264_videotoolbox'

        if is_image:
            # Картинка → видео через GPU
            cmd = [
                'ffmpeg', '-y', '-loop', '1', '-i', str(visual_file),
                '-c:v', encoder,
                '-pix_fmt', 'yuv420p',
                '-t', str(target_seconds),
                '-r', '15',
                '-b:v', '2000k',
                '-allow_sw', '1',
                str(output_path)
            ]
        else:
            # Видео → loop через GPU
            video_duration = self.get_video_duration(visual_file)
            loops = int(target_seconds / video_duration) + 1

            cmd = [
                'ffmpeg', '-y', '-stream_loop', str(loops), '-i', str(visual_file),
                '-c:v', encoder,
                '-pix_fmt', 'yuv420p',
                '-t', str(target_seconds),
                '-r', '15',
                '-b:v', '2000k',
                '-allow_sw', '1',
                str(output_path)
            ]

        logger.info(f"🎨 Создание визуала: {target_duration_hours}h (GPU videotoolbox)")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg ошибка: {result.stderr[:500]}")
            raise RuntimeError("Visual processing failed")

        logger.info(f"✅ Визуал создан: {output_path}")
        return output_path