"""
Library Downloader
Автоматически скачивает classical music из открытых источников
"""
import os
import sys
import time
import random
import logging
import requests
from pathlib import Path
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)

# Определяем корень проекта (где лежит папка scripts/)
SCRIPT_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPT_DIR.parent

class MusopenDownloader:
    """Скачивание с Musopen.org (public domain classical)"""

    BASE_URL = "https://musopen.org"

    COMPOSERS = {
        'chopin': ['nocturne', 'waltz', 'prelude', 'etude', 'ballade'],
        'debussy': ['clair de lune', 'arabesque', 'reverie', 'prelude'],
        'bach': ['goldberg variations', 'well-tempered clavier', 'cello suite'],
        'mozart': ['piano sonata', 'fantasia', 'rondo'],
        'beethoven': ['moonlight sonata', 'pathetique', 'fur elise'],
        'liszt': ['liebestraum', 'consolation', 'etude'],
        'ravel': ['pavane', "jeux d\\'eau", 'sonatine'],
        'satie': ['gymnopedie', 'gnossienne', 'ogive'],
        'tchaikovsky': ['seasons', 'album for the young'],
        'schubert': ['impromptu', 'moment musical'],
    }

    def __init__(self, output_dir=None):
        # Если путь не указан — используем стандартный относительно корня проекта
        if output_dir is None:
            output_dir = PROJECT_ROOT / 'libraries' / 'audio' / 'classical'
        else:
            output_dir = Path(output_dir)

        self.output_dir = output_dir.resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def search_musopen(self, composer, piece_type):
        """Ищет треки на Musopen"""
        query = f"{composer} {piece_type} piano"
        web_search_url = f"{self.BASE_URL}/music/?search={query.replace(' ', '+')}"

        logger.info(f"Поиск: {query}")

        try:
            response = self.session.get(web_search_url, timeout=10)
            import re

            piece_links = re.findall(r'href="(/music/\d+/[^"]+)"', response.text)
            unique_links = list(set(piece_links))[:5]

            return [urljoin(self.BASE_URL, link) for link in unique_links]
        except Exception as e:
            logger.error(f"Ошибка поиска: {e}")
            return []

    def download_from_piece_page(self, piece_url):
        """Скачивает mp3 со страницы композиции"""
        try:
            response = self.session.get(piece_url, timeout=10)
            import re

            mp3_links = re.findall(r'href="(https?://[^"]+\.mp3)"', response.text)

            if not mp3_links:
                mp3_links = re.findall(r'url["\']?\s*:\s*["\'](https?://[^"\']+\.mp3)["\']?', response.text)

            downloaded = []
            for mp3_url in mp3_links[:2]:
                filename = self._sanitize_filename(urlparse(mp3_url).path.split('/')[-1])
                if not filename.endswith('.mp3'):
                    filename += '.mp3'

                output_path = self.output_dir / filename

                if output_path.exists():
                    logger.info(f"Уже скачано: {filename}")
                    downloaded.append(str(output_path))
                    continue

                logger.info(f"Скачивание: {filename}")
                audio_response = self.session.get(mp3_url, stream=True, timeout=30)

                with open(output_path, 'wb') as f:
                    for chunk in audio_response.iter_content(chunk_size=8192):
                        f.write(chunk)

                downloaded.append(str(output_path))
                time.sleep(random.uniform(1, 3))

            return downloaded

        except Exception as e:
            logger.error(f"Ошибка скачивания {piece_url}: {e}")
            return []

    def _sanitize_filename(self, filename):
        """Очищает имя файла"""
        import re
        filename = re.sub(r'[<>:\"/\\|?*]', '_', filename)
        return filename.strip('_')

    def download_composer_collection(self, composer, max_pieces=10):
        """Скачивает коллекцию одного композитора"""
        if composer not in self.COMPOSERS:
            logger.error(f"Неизвестный композитор: {composer}")
            return []

        piece_types = self.COMPOSERS[composer]
        downloaded_all = []

        for piece_type in piece_types:
            if len(downloaded_all) >= max_pieces:
                break

            piece_urls = self.search_musopen(composer, piece_type)

            for url in piece_urls:
                if len(downloaded_all) >= max_pieces:
                    break

                files = self.download_from_piece_page(url)
                downloaded_all.extend(files)
                time.sleep(random.uniform(2, 5))

        logger.info(f"Скачано {len(downloaded_all)} треков {composer}")
        return downloaded_all

    def download_all(self, composers=None, max_per_composer=10):
        """Скачивает библиотеку всех композиторов"""
        composers = composers or list(self.COMPOSERS.keys())
        all_files = []

        for composer in composers:
            files = self.download_composer_collection(composer, max_per_composer)
            all_files.extend(files)
            time.sleep(random.uniform(3, 7))

        logger.info(f"ВСЕГО скачано: {len(all_files)} треков")
        return all_files


class LibraryBuilder:
    """Главный строитель библиотеки"""

    def __init__(self, output_dir=None):
        if output_dir is None:
            output_dir = PROJECT_ROOT / 'libraries' / 'audio' / 'classical'
        else:
            output_dir = Path(output_dir)

        self.output_dir = output_dir.resolve()
        self.musopen = MusopenDownloader(self.output_dir)

    def build_full_library(self, target_count=100):
        """Строит полную библиотеку"""
        logger.info(f"Цель: {target_count} треков")

        composers = ['chopin', 'debussy', 'bach', 'mozart', 'liszt',
                     'ravel', 'satie', 'tchaikovsky', 'beethoven', 'schubert']

        per_composer = target_count // len(composers)
        all_files = []

        for composer in composers:
            files = self.musopen.download_composer_collection(composer, per_composer + 2)
            all_files.extend(files)

            if len(all_files) >= target_count:
                break

        logger.info(f"Готово: {len(all_files)} треков")
        return all_files


def main():
    """CLI для сборки библиотеки"""
    import argparse

    parser = argparse.ArgumentParser(description='Build classical music library')
    parser.add_argument('--count', type=int, default=100, help='Целевое количество треков')
    parser.add_argument('--composer', type=str, help='Конкретный композитор')
    parser.add_argument('--output', type=str, help='Путь к папке (по умолчанию: ../libraries/audio/classical)')

    args = parser.parse_args()

    # Если --output не указан — используем дефолт относительно корня проекта
    output_dir = args.output

    builder = LibraryBuilder(output_dir)

    print(f"📁 Библиотека: {builder.output_dir}")
    print(f"📁 Существует: {builder.output_dir.exists()}")

    if args.composer and args.composer != 'all':
        files = builder.musopen.download_composer_collection(args.composer, args.count)
    else:
        files = builder.build_full_library(args.count)

    print(f"\n✅ Готово! Скачано {len(files)} треков")
    print(f"📁 Сохранено в: {builder.output_dir}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    main()