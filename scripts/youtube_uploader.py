"""
YouTube Uploader
Заливает видео на YouTube через Data API v3
"""
import os
import pickle
import logging
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

logger = logging.getLogger(__name__)

class YouTubeUploader:
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
    API_SERVICE_NAME = 'youtube'
    API_VERSION = 'v3'

    def __init__(self, credentials_path, token_path='token.pickle'):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.youtube = None
        self._authenticate()

    def _authenticate(self):
        """Авторизация через OAuth 2.0"""
        credentials = None

        # Проверяем сохранённый токен
        if self.token_path.exists():
            with open(self.token_path, 'rb') as token:
                credentials = pickle.load(token)

        # Если токен невалиден — обновляем или создаём новый
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    raise FileNotFoundError(
                        f"Credentials не найдены: {self.credentials_path}\n"
                        "Создай через Google Cloud Console и положи сюда."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), self.SCOPES)
                credentials = flow.run_local_server(port=8080)

            # Сохраняем токен
            with open(self.token_path, 'wb') as token:
                pickle.dump(credentials, token)

        self.youtube = build(self.API_SERVICE_NAME, self.API_VERSION, credentials=credentials)
        logger.info("YouTube API аутентификация успешна")

    def upload_video(self, file_path, title, description, tags, category_id='10',
                    privacy_status='public', thumbnail_path=None):
        """
        Заливает видео на YouTube

        Args:
            file_path: путь к видео
            title: название
            description: описание
            tags: список тегов
            category_id: 10 = Music
            privacy_status: public/private/unlisted
            thumbnail_path: путь к превью (опционально)

        Returns:
            video_id
        """
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': category_id
            },
            'status': {
                'privacyStatus': privacy_status,
                'selfDeclaredMadeForKids': False
            }
        }

        media = MediaFileUpload(file_path, resumable=True)

        logger.info(f"Загрузка видео: {title}")

        request = self.youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )

        response = request.execute()
        video_id = response['id']

        logger.info(f"Видео залито: https://youtube.com/watch?v={video_id}")

        # Загружаем thumbnail если есть
        if thumbnail_path and Path(thumbnail_path).exists():
            self.upload_thumbnail(video_id, thumbnail_path)

        return video_id

    def upload_thumbnail(self, video_id, thumbnail_path):
        """Загружает превью для видео"""
        media = MediaFileUpload(thumbnail_path)

        self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=media
        ).execute()

        logger.info(f"Thumbnail загружен для {video_id}")

    def add_to_playlist(self, video_id, playlist_id):
        """Добавляет видео в плейлист"""
        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }

        self.youtube.playlistItems().insert(part='snippet', body=body).execute()
        logger.info(f"Видео {video_id} добавлено в плейлист {playlist_id}")
