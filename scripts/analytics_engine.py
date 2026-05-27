"""
Analytics Engine
Автоматический анализ: какие треки, композиторы, атмосферы работают лучше

Источники данных:
- Локальные логи (какие видео создавались)
- YouTube Analytics API (просмотры, watch time, CTR)
- Сравнительный анализ (A/B тестирование)

Выход:
- Рекомендации по контенту
- Прогнозы производительности
- Авто-корректировка параметров
"""
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Аналитический движок для оптимизации контента"""

    def __init__(self, data_dir='../data', logs_dir='../logs'):
        self.data_dir = Path(data_dir)
        self.logs_dir = Path(logs_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.db_file = self.data_dir / 'video_performance.json'
        self.insights_file = self.data_dir / 'insights.json'

        self.performance_db = self._load_db()

    def _load_db(self):
        """Загружает базу данных производительности"""
        if self.db_file.exists():
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_db(self):
        """Сохраняет базу данных"""
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(self.performance_db, f, indent=2, ensure_ascii=False)

    def record_video_creation(self, video_id, metadata):
        """
        Записывает создание видео в базу

        Args:
            video_id: ID видео (или локальный ID)
            metadata: {composer, mood, activity, duration, title, recipe, immersive}
        """
        self.performance_db[video_id] = {
            'created': datetime.now().isoformat(),
            'metadata': metadata,
            'stats': {
                'views': 0,
                'watch_time_hours': 0,
                'ctr': 0,  # Click-through rate
                'avg_view_duration': 0,
                'likes': 0,
                'comments': 0,
            },
            'performance_score': 0,  # 0-100
        }
        self._save_db()
        logger.info(f"📊 Записано видео: {video_id}")

    def update_video_stats(self, video_id, stats):
        """
        Обновляет статистику видео (из YouTube Analytics API)

        Args:
            stats: {views, watch_time_hours, ctr, avg_view_duration, likes, comments}
        """
        if video_id not in self.performance_db:
            logger.warning(f"Видео не найдено: {video_id}")
            return

        self.performance_db[video_id]['stats'].update(stats)

        # Рассчитываем performance score
        score = self._calculate_performance_score(stats)
        self.performance_db[video_id]['performance_score'] = score

        self._save_db()
        logger.info(f"📊 Обновлена статистика: {video_id} (score: {score})")

    def _calculate_performance_score(self, stats):
        """
        Рассчитывает общий score производительности (0-100)

        Формула:
        - Views: 30% (логарифмическая шкала)
        - Watch time: 40% (самый важный метрик для YouTube)
        - CTR: 20% (привлекательность превью/названия)
        - Engagement (likes+comments): 10%
        """
        views = stats.get('views', 0)
        watch_time = stats.get('watch_time_hours', 0)
        ctr = stats.get('ctr', 0)
        likes = stats.get('likes', 0)
        comments = stats.get('comments', 0)

        # Нормализация (примерные benchmarks)
        views_score = min(30, (views / 10000) * 30)  # 10K views = 30 points
        watch_score = min(40, (watch_time / 500) * 40)  # 500h = 40 points
        ctr_score = min(20, (ctr / 10) * 20)  # 10% CTR = 20 points
        engagement_score = min(10, ((likes + comments) / 500) * 10)

        return round(views_score + watch_score + ctr_score + engagement_score, 1)

    def analyze_by_composer(self):
        """Анализирует производительность по композиторам"""
        composer_stats = defaultdict(lambda: {
            'count': 0, 'total_views': 0, 'total_watch_time': 0,
            'avg_score': 0, 'scores': []
        })

        for video_id, data in self.performance_db.items():
            composer = data['metadata'].get('composer', 'unknown')
            stats = data['stats']
            score = data['performance_score']

            composer_stats[composer]['count'] += 1
            composer_stats[composer]['total_views'] += stats.get('views', 0)
            composer_stats[composer]['total_watch_time'] += stats.get('watch_time_hours', 0)
            composer_stats[composer]['scores'].append(score)

        # Считаем средние
        for composer, data in composer_stats.items():
            if data['scores']:
                data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 1)

        # Сортируем по avg_score
        return dict(sorted(composer_stats.items(), 
                          key=lambda x: x[1]['avg_score'], reverse=True))

    def analyze_by_mood(self):
        """Анализирует производительность по настроениям"""
        mood_stats = defaultdict(lambda: {
            'count': 0, 'total_views': 0, 'avg_score': 0, 'scores': []
        })

        for video_id, data in self.performance_db.items():
            mood = data['metadata'].get('mood', 'unknown')
            stats = data['stats']
            score = data['performance_score']

            mood_stats[mood]['count'] += 1
            mood_stats[mood]['total_views'] += stats.get('views', 0)
            mood_stats[mood]['scores'].append(score)

        for mood, data in mood_stats.items():
            if data['scores']:
                data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 1)

        return dict(sorted(mood_stats.items(), 
                          key=lambda x: x[1]['avg_score'], reverse=True))

    def analyze_by_recipe(self):
        """Анализирует производительность по immersive-рецептам"""
        recipe_stats = defaultdict(lambda: {
            'count': 0, 'total_views': 0, 'avg_score': 0, 'scores': []
        })

        for video_id, data in self.performance_db.items():
            recipe = data['metadata'].get('recipe', 'none')
            stats = data['stats']
            score = data['performance_score']

            recipe_stats[recipe]['count'] += 1
            recipe_stats[recipe]['total_views'] += stats.get('views', 0)
            recipe_stats[recipe]['scores'].append(score)

        for recipe, data in recipe_stats.items():
            if data['scores']:
                data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 1)

        return dict(sorted(recipe_stats.items(), 
                          key=lambda x: x[1]['avg_score'], reverse=True))

    def analyze_by_duration(self):
        """Анализирует оптимальную длительность"""
        duration_stats = defaultdict(lambda: {
            'count': 0, 'avg_score': 0, 'scores': []
        })

        for video_id, data in self.performance_db.items():
            duration = data['metadata'].get('duration', 2)
            score = data['performance_score']

            duration_stats[duration]['count'] += 1
            duration_stats[duration]['scores'].append(score)

        for duration, data in duration_stats.items():
            if data['scores']:
                data['avg_score'] = round(sum(data['scores']) / len(data['scores']), 1)

        return dict(sorted(duration_stats.items(), 
                          key=lambda x: x[1]['avg_score'], reverse=True))

    def get_insights(self):
        """
        Генерирует actionable insights

        Returns:
            list of dicts: {type, message, confidence, action}
        """
        insights = []

        # Анализ композиторов
        composer_data = self.analyze_by_composer()
        if composer_data:
            top_composer = list(composer_data.keys())[0]
            top_score = composer_data[top_composer]['avg_score']

            if top_score > 50:
                insights.append({
                    'type': 'composer',
                    'message': f"🎹 {top_composer.title()} показывает лучшие результаты (score: {top_score})",
                    'confidence': 'high',
                    'action': f"Увеличь долю {top_composer} в контенте до 40%"
                })

        # Анализ настроений
        mood_data = self.analyze_by_mood()
        if mood_data:
            top_mood = list(mood_data.keys())[0]
            insights.append({
                'type': 'mood',
                'message': f"🎭 Настроение '{top_mood}' — самое популярное",
                'confidence': 'medium',
                'action': f"Создай серию видео '{top_mood} + разные композиторы'"
            })

        # Анализ рецептов
        recipe_data = self.analyze_by_recipe()
        if recipe_data:
            immersive_recipes = {k: v for k, v in recipe_data.items() if k != 'none'}
            if immersive_recipes:
                top_recipe = list(immersive_recipes.keys())[0]
                insights.append({
                    'type': 'recipe',
                    'message': f"🎧 Immersive рецепт '{top_recipe}' outperform обычный audio",
                    'confidence': 'high',
                    'action': "Используй immersive для всех новых видео"
                })

        # Анализ длительности
        duration_data = self.analyze_by_duration()
        if duration_data:
            top_duration = list(duration_data.keys())[0]
            insights.append({
                'type': 'duration',
                'message': f"⏱️ Оптимальная длительность: {top_duration} часа",
                'confidence': 'medium',
                'action': f"Фокусируйся на {top_duration}h видео"
            })

        # Анализ CTR (если есть данные)
        low_ctr_videos = [
            vid for vid, data in self.performance_db.items()
            if data['stats'].get('ctr', 0) < 2 and data['stats'].get('views', 0) > 100
        ]
        if len(low_ctr_videos) > 3:
            insights.append({
                'type': 'ctr',
                'message': f"📉 {len(low_ctr_videos)} видео с низким CTR (< 2%)",
                'confidence': 'high',
                'action': "Пересмотри thumbnail и названия для этих видео"
            })

        return insights

    def generate_recommendations(self):
        """
        Генерирует конкретные рекомендации для следующих видео

        Returns:
            dict: {next_composer, next_mood, next_duration, next_recipe, reasoning}
        """
        composer_data = self.analyze_by_composer()
        mood_data = self.analyze_by_mood()
        duration_data = self.analyze_by_duration()
        recipe_data = self.analyze_by_recipe()

        # Top performers
        top_composer = list(composer_data.keys())[0] if composer_data else 'chopin'
        top_mood = list(mood_data.keys())[0] if mood_data else 'melancholic'
        top_duration = list(duration_data.keys())[0] if duration_data else 2

        # Выбираем лучший immersive рецепт
        immersive_recipes = {k: v for k, v in recipe_data.items() if k != 'none'}
        top_recipe = list(immersive_recipes.keys())[0] if immersive_recipes else 'cozy_study'

        # Иногда добавляем вариацию (не всегда топ)
        if len(composer_data) > 2 and random.random() > 0.7:
            # 30% шанс взять #2 композитора для разнообразия
            top_composer = list(composer_data.keys())[1]

        return {
            'next_composer': top_composer,
            'next_mood': top_mood,
            'next_duration': top_duration,
            'next_recipe': top_recipe,
            'reasoning': f"На основе анализа {len(self.performance_db)} видео: "
                        f"{top_composer} (score: {composer_data.get(top_composer, {}).get('avg_score', 0)}), "
                        f"{top_mood} — лучшее настроение, "
                        f"{top_recipe} — лучший immersive рецепт"
        }

    def export_report(self, output_path='../data/analytics_report.json'):
        """Экспортирует полный отчёт"""
        report = {
            'generated': datetime.now().isoformat(),
            'total_videos': len(self.performance_db),
            'composer_analysis': self.analyze_by_composer(),
            'mood_analysis': self.analyze_by_mood(),
            'recipe_analysis': self.analyze_by_recipe(),
            'duration_analysis': self.analyze_by_duration(),
            'insights': self.get_insights(),
            'recommendations': self.generate_recommendations(),
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Отчёт экспортирован: {output_path}")
        return report

    def print_dashboard(self):
        """Печатает текстовый дашборд в консоль"""
        print("\n" + "=" * 60)
        print("📊 ANALYTICS DASHBOARD")
        print("=" * 60)

        print(f"\n📹 Total Videos: {len(self.performance_db)}")

        # Composers
        print("\n🎹 Top Composers:")
        for composer, data in list(self.analyze_by_composer().items())[:5]:
            print(f"   {composer.title():12} | Score: {data['avg_score']:5.1f} | "
                  f"Videos: {data['count']:3} | Views: {data['total_views']:,}")

        # Moods
        print("\n🎭 Top Moods:")
        for mood, data in list(self.analyze_by_mood().items())[:5]:
            print(f"   {mood.title():12} | Score: {data['avg_score']:5.1f} | "
                  f"Videos: {data['count']:3}")

        # Insights
        print("\n💡 Insights:")
        for insight in self.get_insights():
            print(f"   [{insight['confidence'].upper()}] {insight['message']}")
            print(f"            → {insight['action']}")

        # Recommendations
        rec = self.generate_recommendations()
        print(f"\n🎯 Next Video Recommendation:")
        print(f"   Composer: {rec['next_composer'].title()}")
        print(f"   Mood: {rec['next_mood'].title()}")
        print(f"   Duration: {rec['next_duration']}h")
        print(f"   Recipe: {rec['next_recipe']}")
        print(f"   Reason: {rec['reasoning']}")

        print("\n" + "=" * 60)


def main():
    """CLI для аналитики"""
    import argparse

    parser = argparse.ArgumentParser(description='Analytics Engine')
    parser.add_argument('--dashboard', action='store_true', help='Показать дашборд')
    parser.add_argument('--export', type=str, help='Экспортировать отчёт')
    parser.add_argument('--recommend', action='store_true', help='Показать рекомендации')

    args = parser.parse_args()

    engine = AnalyticsEngine()

    if args.dashboard:
        engine.print_dashboard()

    if args.export:
        engine.export_report(args.export)
        print(f"✅ Отчёт сохранён: {args.export}")

    if args.recommend:
        rec = engine.generate_recommendations()
        print("\n🎯 Рекомендации для следующего видео:")
        for key, value in rec.items():
            print(f"   {key}: {value}")

    if not any([args.dashboard, args.export, args.recommend]):
        engine.print_dashboard()

if __name__ == '__main__':
    import random
    logging.basicConfig(level=logging.INFO)
    main()
