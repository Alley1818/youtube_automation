"""
AI Title Generator
Генерирует оригинальные, не-кринжовые названия через LLM API
"""
import os
import json
import random
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class AITitleGenerator:
    """Генератор названий через AI API"""

    GOOD_EXAMPLES = [
        "a playlist for those born in the wrong century",
        "you come from old money, but it's 1948",
        "royal is falling in love with you",
        "slow living in a parisian apartment",
        "a love letter to rainy afternoons",
        "the library at 3am, and someone is playing piano downstairs",
        "for when you miss a place you've never been",
        "the last dance at the vienna cafe, 1924",
        "someone left the window open, and chopin walked in",
        "the kind of sadness that wears a tuxedo",
    ]

    def __init__(self, api_provider='gemini'):
        self.api_provider = api_provider
        self.api_key = self._get_api_key()
        self.fallback_generator = FallbackTitleGenerator()

    def _get_api_key(self):
        """Получает API ключ из env"""
        if self.api_provider == 'gemini':
            return os.getenv('GEMINI_API_KEY', '')
        elif self.api_provider == 'openrouter':
            return os.getenv('OPENROUTER_API_KEY', '')
        return ''

    def generate_with_gemini(self, composer, mood, activity, duration):
        """Генерация через Google Gemini"""
        if not self.api_key:
            return None

        prompt = f"""You are a poetic, subtle title creator for a YouTube classical piano channel. 
The channel aesthetic is "dark academia" and "old money" — but NEVER use those words directly.

Create a title for a {duration}-hour {mood} piano playlist by {composer.title()}.
The title should feel like:
- A whispered secret
- A memory of something beautiful
- A scene from a forgotten novel
- An emotion that doesn't have a name

Rules:
- NO hashtags, NO emojis
- NO words like: vibes, aesthetic, playlist (unless subtle)
- NO capital letters (except names)
- Length: 5-12 words
- Make it feel intimate, not performative

Examples of the style:
{chr(10).join(f'  - "{ex}"' for ex in random.sample(self.GOOD_EXAMPLES, 5))}

Now create ONE title for: {composer} + {mood} + {activity}
Return ONLY the title, nothing else."""

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 50
                }
            }

            response = requests.post(url, json=payload, timeout=15)
            data = response.json()

            if 'candidates' in data:
                title = data['candidates'][0]['content']['parts'][0]['text'].strip()
                # Чистим кавычки
                title = title.strip('"').strip("'")
                return title

            return None

        except Exception as e:
            logger.warning(f"Gemini API error: {e}")
            return None

    def generate_with_openrouter(self, composer, mood, activity, duration):
        """Генерация через OpenRouter"""
        if not self.api_key:
            return None

        prompt = f"""Create a poetic, understated title for a {duration}-hour {mood} classical piano video featuring {composer}.
Style: intimate, literary, nostalgic. No hashtags, no emojis, no words like 'vibes' or 'aesthetic'.
Lowercase. 5-12 words. Like a sentence from a diary.

Examples:
{chr(10).join(random.sample(self.GOOD_EXAMPLES, 3))}

Title:"""

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "mistralai/mistral-7b-instruct:free",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.9,
                    "max_tokens": 50
                },
                timeout=15
            )

            data = response.json()
            if 'choices' in data:
                title = data['choices'][0]['message']['content'].strip()
                title = title.strip('"').strip("'")
                return title

            return None

        except Exception as e:
            logger.warning(f"OpenRouter API error: {e}")
            return None

    def generate(self, composer, mood, activity, duration, use_ai=True):
        """Генерирует название"""
        if use_ai and self.api_key:
            if self.api_provider == 'gemini':
                title = self.generate_with_gemini(composer, mood, activity, duration)
            elif self.api_provider == 'openrouter':
                title = self.generate_with_openrouter(composer, mood, activity, duration)
            else:
                title = None

            if title:
                logger.info(f"AI generated title: {title}")
                return title

        # Fallback
        return self.fallback_generator.generate(composer, mood, activity, duration)


class FallbackTitleGenerator:
    """Продвинутый fallback без API"""

    FRAGMENTS = {
        'openers': [
            "the last", "someone left", "a forgotten", "the distant",
            "for when", "the kind of", "between", "after midnight",
            "the window", "a room where", "the silence", "your grandfather's",
            "the candle", "a letter", "the rain", "the ghost of",
            "every", "the old", "a memory", "the piano",
        ],
        'middles': [
            "time you", "light still", "song that", "room still",
            "you remember", "nobody", "everything", "the books",
            "someone", "the walls", "the clock", "winter",
            "echoes", "shadows", "dust", "gold", "ivory",
        ],
        'closers': [
            "burns", "listens", "waits", "knows", "lingers",
            "remains", "returns", "falls", "speaks", "stays",
            "dances", "weeps", "dreams", "plays on",
        ],
        'scenes': [
            "at 3am", "in vienna", "by the window", "under candlelight",
            "while it rains", "in an empty house", "before dawn",
            "after everyone left", "in the library", "by the fireplace",
        ],
        'emotions': [
            "the sadness", "the longing", "the quiet", "the warmth",
            "the weight", "the softness", "the ache", "the peace",
        ]
    }

    TEMPLATES = [
        "{opener} {middle} {closer}",
        "{opener} {scene}",
        "{emotion} that {middle} {closer}",
        "{opener} {scene}, and {middle} {closer}",
        "{scene}, {opener} {middle}",
        "{opener} {middle} {scene}",
        "{emotion} {scene}",
        "{opener} {closer} {scene}",
    ]

    def generate(self, composer, mood, activity, duration):
        """Генерирует название из фрагментов"""
        template = random.choice(self.TEMPLATES)

        parts = {
            'opener': random.choice(self.FRAGMENTS['openers']),
            'middle': random.choice(self.FRAGMENTS['middles']),
            'closer': random.choice(self.FRAGMENTS['closers']),
            'scene': random.choice(self.FRAGMENTS['scenes']),
            'emotion': random.choice(self.FRAGMENTS['emotions']),
        }

        title = template.format(**parts)

        # Добавляем композитора тонко
        endings = [
            f" (a {composer} evening)",
            f", according to {composer}",
            f" — {composer} understands",
            f"",
            f", {composer} playing somewhere",
        ]

        title += random.choice(endings)

        # Добавляем длительность если нужно
        if random.random() > 0.5:
            title += f" • {duration}h"

        return title.lower().strip()


def main():
    """CLI тест генератора"""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--composer', default='chopin')
    parser.add_argument('--mood', default='melancholic')
    parser.add_argument('--activity', default='studying')
    parser.add_argument('--duration', type=float, default=2)
    parser.add_argument('--count', type=int, default=10)
    parser.add_argument('--provider', default='fallback', choices=['gemini', 'openrouter', 'fallback'])

    args = parser.parse_args()

    gen = AITitleGenerator(api_provider=args.provider)

    print(f"\n🎨 Генерация {args.count} названий ({args.provider}):\n")
    for i in range(args.count):
        title = gen.generate(args.composer, args.mood, args.activity, args.duration, use_ai=True)
        print(f"  {i+1}. {title}")

    print("\n✅ Готово!")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()