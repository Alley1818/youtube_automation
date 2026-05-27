"""
Audio Processor
Обрабатывает аудио: loop до нужной длительности, fade in/out, normalize
"""
import os
import random
import subprocess
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self, audio_library_path):
        self.audio_library = Path(audio_library_path)
        self.audio_files = []
        self._scan_library()

    def _scan_library(self):
        """Сканирует библиотеку аудио"""
        extensions = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')
        self.audio_files = [
            f for f in self.audio_library.rglob('*') 
            if f.suffix.lower() in extensions
        ]
        logger.info(f"Найдено аудио файлов: {len(self.audio_files)}")

    def get_random_audio(self, count=1):
        """Выбирает случайные треки"""
        if not self.audio_files:
            raise ValueError("Библиотека аудио пуста!")
        selected = random.sample(self.audio_files, min(count, len(self.audio_files)))
        return selected

    def get_audio_duration(self, audio_path):
        """Получает длительность аудио в секундах"""
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_path)
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return float(result.stdout.strip())

    def create_long_audio(self, audio_files, target_duration_hours, output_path, 
                         fade_in=5, fade_out=5):
        """
        Создаёт длинное аудио путём loop'а треков

        Args:
            audio_files: список Path к аудио файлам
            target_duration_hours: целевая длительность в часах
            output_path: куда сохранить
            fade_in: секунд fade in
            fade_out: секунд fade out
        """
        target_seconds = target_duration_hours * 3600

        # Создаём файл со списком для concat
        temp_dir = Path(output_path).parent / "temp"
        temp_dir.mkdir(exist_ok=True)
        list_file = temp_dir / "audio_list.txt"

        # Считаем сколько раз нужно повторить
        total_duration = 0
        loops_needed = []

        for audio in audio_files:
            duration = self.get_audio_duration(audio)
            loops_needed.append({
                'path': audio,
                'duration': duration
            })
            total_duration += duration

        # Если один трек короче целевой длительности — loop'аем его
        if len(audio_files) == 1 and total_duration < target_seconds:
            single_audio = audio_files[0]
            single_duration = self.get_audio_duration(single_audio)
            repeats = int(target_seconds / single_duration) + 1

            with open(list_file, 'w', encoding='utf-8') as f:
                for _ in range(repeats):
                    f.write(f"file '{single_audio.absolute().as_posix()}'\n")
        else:
            # Смешиваем несколько треков, повторяя пока не достигнем целевой длительности
            with open(list_file, 'w', encoding='utf-8') as f:
                current_duration = 0
                track_index = 0
                while current_duration < target_seconds:
                    audio = audio_files[track_index % len(audio_files)]
                    f.write(f"file '{audio.absolute().as_posix()}'\n")
                    current_duration += loops_needed[track_index % len(audio_files)]['duration']
                    track_index += 1

        # FFmpeg concat + fade + normalize
        cmd = [
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
            '-i', str(list_file),
            '-af', f'afade=t=in:ss=0:d={fade_in},afade=t=out:st={target_seconds-fade_out}:d={fade_out},loudnorm=I=-16:TP=-1.5:LRA=11',
            '-t', str(target_seconds),
            '-c:a', 'libmp3lame', '-b:a', '192k',
            str(output_path)
        ]

        logger.info(f"Создание аудио: {target_duration_hours}h -> {output_path}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"FFmpeg ошибка: {result.stderr}")
            raise RuntimeError(f"Audio processing failed: {result.stderr}")

        # Очистка temp
        list_file.unlink(missing_ok=True)

        logger.info(f"Аудио создано: {output_path}")
        return output_path
