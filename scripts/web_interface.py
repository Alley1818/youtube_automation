"""
Web Interface for Classical Piano Automation Agent
Flask-based dashboard для управления без командной строки

Запуск:
    python web_interface.py
    Открыть: http://localhost:5000
"""
import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__)
app.secret_key = 'classical-piano-agent-2026'

BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / 'logs'
OUTPUT_DIR = BASE_DIR / 'output'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────
# HTML TEMPLATE (inline для автономности)
# ───────────────────────────────────────────────
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Classical Piano Agent — Control Panel</title>
    <style>
        :root {
            --bg: #0f0f1a;
            --bg-card: #1a1a2e;
            --bg-input: #16213e;
            --text: #e0e0e0;
            --text-muted: #888;
            --gold: #d4af37;
            --gold-dim: #8b7355;
            --accent: #c9a227;
            --success: #4caf50;
            --error: #f44336;
            --warning: #ff9800;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            line-height: 1.6;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid var(--gold-dim);
            margin-bottom: 30px;
        }

        header h1 {
            font-size: 2.5rem;
            color: var(--gold);
            font-weight: 400;
            letter-spacing: 2px;
        }

        header p {
            color: var(--text-muted);
            margin-top: 10px;
            font-style: italic;
        }

        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }

        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
        }

        .card {
            background: var(--bg-card);
            border: 1px solid var(--gold-dim);
            border-radius: 8px;
            padding: 25px;
        }

        .card h2 {
            color: var(--gold);
            font-size: 1.3rem;
            margin-bottom: 20px;
            font-weight: 400;
        }

        .form-group {
            margin-bottom: 18px;
        }

        label {
            display: block;
            color: var(--text-muted);
            margin-bottom: 6px;
            font-size: 0.9rem;
        }

        select, input[type="number"], input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            background: var(--bg-input);
            border: 1px solid var(--gold-dim);
            border-radius: 4px;
            color: var(--text);
            font-family: inherit;
            font-size: 1rem;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--gold);
        }

        .checkbox-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            margin-top: 8px;
        }

        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
            cursor: pointer;
        }

        .checkbox-item input[type="checkbox"] {
            width: 18px;
            height: 18px;
            accent-color: var(--gold);
        }

        .btn {
            display: inline-block;
            padding: 14px 32px;
            background: var(--gold);
            color: var(--bg);
            border: none;
            border-radius: 4px;
            font-family: inherit;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            letter-spacing: 1px;
        }

        .btn:hover {
            background: var(--accent);
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(212, 175, 55, 0.3);
        }

        .btn:disabled {
            background: var(--gold-dim);
            cursor: not-allowed;
            transform: none;
        }

        .btn-secondary {
            background: transparent;
            border: 1px solid var(--gold);
            color: var(--gold);
        }

        .btn-secondary:hover {
            background: var(--gold);
            color: var(--bg);
        }

        .status-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .status-item {
            background: var(--bg-card);
            border: 1px solid var(--gold-dim);
            padding: 12px 20px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--success);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .log-terminal {
            background: #000;
            border: 1px solid var(--gold-dim);
            border-radius: 4px;
            padding: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            height: 300px;
            overflow-y: auto;
            color: #4caf50;
        }

        .log-terminal .error { color: var(--error); }
        .log-terminal .warning { color: var(--warning); }
        .log-terminal .info { color: #64b5f6; }

        .video-list {
            display: grid;
            gap: 10px;
        }

        .video-item {
            background: var(--bg-input);
            padding: 12px 15px;
            border-radius: 4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .video-item .title {
            color: var(--text);
            font-size: 0.9rem;
        }

        .video-item .meta {
            color: var(--text-muted);
            font-size: 0.8rem;
        }

        .tabs {
            display: flex;
            gap: 5px;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--gold-dim);
        }

        .tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            color: var(--text-muted);
            font-family: inherit;
            font-size: 1rem;
            cursor: pointer;
            border-bottom: 2px solid transparent;
            transition: all 0.3s;
        }

        .tab.active {
            color: var(--gold);
            border-bottom-color: var(--gold);
        }

        .tab:hover {
            color: var(--text);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: var(--bg-input);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 10px;
        }

        .progress-fill {
            height: 100%;
            background: var(--gold);
            width: 0%;
            transition: width 0.3s ease;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }

        @media (max-width: 768px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--gold-dim);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }

        .stat-value {
            font-size: 2rem;
            color: var(--gold);
            font-weight: 600;
        }

        .stat-label {
            color: var(--text-muted);
            font-size: 0.85rem;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>♪ Classical Piano Agent</h1>
            <p>Automated video creation in the style of Dear Victor and Victoria</p>
        </header>

        <div class="status-bar">
            <div class="status-item">
                <div class="status-dot"></div>
                <span>Agent Ready</span>
            </div>
            <div class="status-item">
                <span>🎵 Audio Library: {{ audio_count }} tracks</span>
            </div>
            <div class="status-item">
                <span>🎨 Visual Library: {{ visual_count }} files</span>
            </div>
            <div class="status-item">
                <span>📹 Videos Created: {{ video_count }}</span>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('create')">🎬 Create Video</button>
            <button class="tab" onclick="showTab('batch')">📦 Batch Mode</button>
            <button class="tab" onclick="showTab('analytics')">📊 Analytics</button>
            <button class="tab" onclick="showTab('library')">📚 Library</button>
        </div>

        <!-- CREATE TAB -->
        <div id="create" class="tab-content active">
            <div class="grid">
                <div class="card">
                    <h2>Video Settings</h2>
                    <form id="createForm" onsubmit="createVideo(event)">
                        <div class="form-group">
                            <label>Composer</label>
                            <select name="composer" id="composer">
                                <option value="random">🎲 Random</option>
                                <option value="chopin">Chopin</option>
                                <option value="debussy">Debussy</option>
                                <option value="bach">Bach</option>
                                <option value="mozart">Mozart</option>
                                <option value="liszt">Liszt</option>
                                <option value="ravel">Ravel</option>
                                <option value="satie">Satie</option>
                                <option value="tchaikovsky">Tchaikovsky</option>
                                <option value="beethoven">Beethoven</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Duration (hours)</label>
                            <select name="duration" id="duration">
                                <option value="1.5">1.5 hours</option>
                                <option value="2" selected>2 hours</option>
                                <option value="3">3 hours</option>
                                <option value="5">5 hours</option>
                                <option value="8">8 hours</option>
                                <option value="10">10 hours</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Mood</label>
                            <select name="mood" id="mood">
                                <option value="random">🎲 Random</option>
                                <option value="melancholic" selected>Melancholic</option>
                                <option value="ethereal">Ethereal</option>
                                <option value="nostalgic">Nostalgic</option>
                                <option value="dreamy">Dreamy</option>
                                <option value="serene">Serene</option>
                                <option value="peaceful">Peaceful</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Activity</label>
                            <select name="activity" id="activity">
                                <option value="random">🎲 Random</option>
                                <option value="studying" selected>Studying</option>
                                <option value="reading">Reading</option>
                                <option value="sleeping">Sleeping</option>
                                <option value="focus">Focus</option>
                                <option value="contemplation">Contemplation</option>
                                <option value="rainy days">Rainy Days</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>Options</label>
                            <div class="checkbox-group">
                                <label class="checkbox-item">
                                    <input type="checkbox" name="immersive" id="immersive" checked>
                                    <span>🎧 Immersive Audio</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" name="ai_titles" id="ai_titles" checked>
                                    <span>🤖 AI Titles</span>
                                </label>
                                <label class="checkbox-item">
                                    <input type="checkbox" name="auto_upload" id="auto_upload" checked>
                                    <span>📤 Auto Upload</span>
                                </label>
                            </div>
                        </div>

                        <button type="submit" class="btn" id="createBtn">
                            🎬 Create & Upload Video
                        </button>

                        <div class="progress-bar" id="progressBar" style="display:none;">
                            <div class="progress-fill" id="progressFill"></div>
                        </div>
                    </form>
                </div>

                <div class="card">
                    <h2>Live Log</h2>
                    <div class="log-terminal" id="logTerminal">
                        <span class="info">[{{ now }}] Agent initialized...</span><br>
                        <span class="info">[{{ now }}] Ready to create videos.</span><br>
                        <span class="info">[{{ now }}] Audio library: {{ audio_count }} tracks loaded.</span><br>
                        <span class="info">[{{ now }}] Visual library: {{ visual_count }} files loaded.</span><br>
                    </div>
                </div>
            </div>
        </div>

        <!-- BATCH TAB -->
        <div id="batch" class="tab-content">
            <div class="card">
                <h2>Batch Creation</h2>
                <p style="color: var(--text-muted); margin-bottom: 20px;">
                    Create multiple videos automatically. Each will have random parameters.
                </p>

                <form onsubmit="createBatch(event)">
                    <div class="form-group">
                        <label>Number of Videos</label>
                        <input type="number" name="batch_count" value="7" min="1" max="30">
                    </div>

                    <div class="form-group">
                        <label>Default Duration</label>
                        <select name="batch_duration">
                            <option value="1.5">1.5 hours</option>
                            <option value="2" selected>2 hours</option>
                            <option value="3">3 hours</option>
                        </select>
                    </div>

                    <div class="checkbox-group" style="margin-bottom: 20px;">
                        <label class="checkbox-item">
                            <input type="checkbox" name="batch_immersive" checked>
                            <span>Immersive Audio</span>
                        </label>
                        <label class="checkbox-item">
                            <input type="checkbox" name="batch_ai" checked>
                            <span>AI Titles</span>
                        </label>
                    </div>

                    <button type="submit" class="btn">📦 Create Batch</button>
                    <button type="button" class="btn btn-secondary" onclick="scheduleDaily()">📅 Schedule Daily</button>
                </form>
            </div>
        </div>

        <!-- ANALYTICS TAB -->
        <div id="analytics" class="tab-content">
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ total_videos }}</div>
                    <div class="stat-label">Total Videos</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ total_views }}</div>
                    <div class="stat-label">Total Views</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ avg_duration }}</div>
                    <div class="stat-label">Avg Watch Time</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ top_composer }}</div>
                    <div class="stat-label">Top Composer</div>
                </div>
            </div>

            <div class="grid">
                <div class="card">
                    <h2>Performance by Composer</h2>
                    <div id="composerChart" style="height: 250px;">
                        <!-- Simple bar chart via CSS -->
                        {% for composer, views in composer_stats.items() %}
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="color: var(--text-muted);">{{ composer.title() }}</span>
                                <span style="color: var(--gold);">{{ views }} views</span>
                            </div>
                            <div style="background: var(--bg-input); height: 8px; border-radius: 4px;">
                                <div style="background: var(--gold); height: 100%; border-radius: 4px; width: {{ views / max_views * 100 }}%;"></div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="card">
                    <h2>Performance by Mood</h2>
                    <div id="moodChart" style="height: 250px;">
                        {% for mood, count in mood_stats.items() %}
                        <div style="margin-bottom: 10px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                                <span style="color: var(--text-muted);">{{ mood.title() }}</span>
                                <span style="color: var(--gold);">{{ count }} videos</span>
                            </div>
                            <div style="background: var(--bg-input); height: 8px; border-radius: 4px;">
                                <div style="background: var(--accent); height: 100%; border-radius: 4px; width: {{ count / max_mood * 100 }}%;"></div>
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
            </div>
        </div>

        <!-- LIBRARY TAB -->
        <div id="library" class="tab-content">
            <div class="grid">
                <div class="card">
                    <h2>Recent Videos</h2>
                    <div class="video-list">
                        {% for video in recent_videos %}
                        <div class="video-item">
                            <div>
                                <div class="title">{{ video.title[:50] }}...</div>
                                <div class="meta">{{ video.composer }} | {{ video.duration }}h | {{ video.created }}</div>
                            </div>
                            <div class="meta">
                                {% if video.youtube_id %}
                                <a href="https://youtube.com/watch?v={{ video.youtube_id }}" target="_blank" style="color: var(--gold);">🔗 View</a>
                                {% else %}
                                <span style="color: var(--text-muted);">Local</span>
                                {% endif %}
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </div>

                <div class="card">
                    <h2>Library Status</h2>
                    <div class="video-list">
                        <div class="video-item">
                            <span>🎵 Classical Audio</span>
                            <span style="color: var(--gold);">{{ audio_count }} files</span>
                        </div>
                        <div class="video-item">
                            <span>🔥 Fireplace SFX</span>
                            <span style="color: var(--gold);">{{ sfx_fire }} files</span>
                        </div>
                        <div class="video-item">
                            <span>🌧️ Rain SFX</span>
                            <span style="color: var(--gold);">{{ sfx_rain }} files</span>
                        </div>
                        <div class="video-item">
                            <span>🎨 Visual Assets</span>
                            <span style="color: var(--gold);">{{ visual_count }} files</span>
                        </div>
                    </div>

                    <div style="margin-top: 20px;">
                        <button class="btn btn-secondary" onclick="downloadLibrary()" style="width: 100%;">
                            ⬇️ Download More Assets
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }

        function addLog(message, type = 'info') {
            const terminal = document.getElementById('logTerminal');
            const time = new Date().toLocaleTimeString();
            const span = document.createElement('span');
            span.className = type;
            span.innerHTML = `[${time}] ${message}<br>`;
            terminal.appendChild(span);
            terminal.scrollTop = terminal.scrollHeight;
        }

        async function createVideo(event) {
            event.preventDefault();
            const btn = document.getElementById('createBtn');
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');

            btn.disabled = true;
            progressBar.style.display = 'block';
            addLog('Starting video creation...', 'info');

            const formData = new FormData(event.target);
            const data = Object.fromEntries(formData);

            try {
                progressFill.style.width = '20%';
                addLog('Generating metadata...', 'info');

                const response = await fetch('/api/create', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });

                progressFill.style.width = '60%';
                addLog('Processing audio & visual...', 'info');

                const result = await response.json();

                progressFill.style.width = '100%';
                if (result.success) {
                    addLog(`✅ Video created: ${result.title}`, 'info');
                    if (result.youtube_url) {
                        addLog(`📤 Uploaded: ${result.youtube_url}`, 'info');
                    }
                } else {
                    addLog(`❌ Error: ${result.error}`, 'error');
                }
            } catch (e) {
                addLog(`❌ Error: ${e.message}`, 'error');
            } finally {
                btn.disabled = false;
                setTimeout(() => {
                    progressBar.style.display = 'none';
                    progressFill.style.width = '0%';
                }, 3000);
            }
        }

        async function createBatch(event) {
            event.preventDefault();
            addLog('Starting batch creation...', 'warning');
            // Implementation similar to createVideo
        }

        function scheduleDaily() {
            addLog('Scheduled daily creation at 10:00 AM', 'info');
            alert('Daily creation scheduled! Check your system cron.');
        }

        function downloadLibrary() {
            addLog('Opening library downloader...', 'info');
            window.open('/api/download-library', '_blank');
        }
    </script>
</body>
</html>
"""

# ───────────────────────────────────────────────
# FLASK ROUTES
# ───────────────────────────────────────────────

def get_library_counts():
    """Считает файлы в библиотеках"""
    audio_dir = BASE_DIR / 'libraries/audio/classical'
    visual_dir = BASE_DIR / 'libraries/visual'
    sfx_fire = BASE_DIR / 'libraries/audio/sfx/fireplace'
    sfx_rain = BASE_DIR / 'libraries/audio/sfx/rain'
    output_dir = BASE_DIR / 'output'

    return {
        'audio_count': len(list(audio_dir.glob('*'))),
        'visual_count': len(list(visual_dir.rglob('*'))),
        'sfx_fire': len(list(sfx_fire.glob('*'))) if sfx_fire.exists() else 0,
        'sfx_rain': len(list(sfx_rain.glob('*'))) if sfx_rain.exists() else 0,
        'video_count': len([f for f in output_dir.glob('*') if f.suffix == '.mp4']),
    }

def get_recent_videos():
    """Получает список последних видео"""
    output_dir = BASE_DIR / 'output'
    videos = []

    for f in sorted(output_dir.glob('*.mp4'), key=lambda x: x.stat().st_mtime, reverse=True)[:10]:
        stat = f.stat()
        videos.append({
            'title': f.stem.replace('_', ' ').title(),
            'composer': 'Unknown',
            'duration': '2',
            'created': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M'),
            'youtube_id': None,
        })

    return videos

@app.route('/')
def index():
    """Главная страница"""
    counts = get_library_counts()
    recent = get_recent_videos()
    now = datetime.now().strftime('%H:%M:%S')

    # Mock analytics data (в реальности — из БД или файлов)
    composer_stats = {
        'chopin': 12450, 'debussy': 8930, 'bach': 10200,
        'mozart': 7800, 'liszt': 5600, 'ravel': 4300
    }
    mood_stats = {
        'melancholic': 15, 'ethereal': 12, 'nostalgic': 10,
        'dreamy': 8, 'serene': 7, 'peaceful': 5
    }

    return render_template_string(HTML_TEMPLATE,
        now=now,
        **counts,
        recent_videos=recent,
        total_videos=counts['video_count'],
        total_views='156.2K',
        avg_duration='1:42:30',
        top_composer='Chopin',
        composer_stats=composer_stats,
        mood_stats=mood_stats,
        max_views=max(composer_stats.values()),
        max_mood=max(mood_stats.values()),
    )

@app.route('/api/create', methods=['POST'])
def api_create():
    """API endpoint для создания видео"""
    data = request.json

    try:
        # Формируем команду
        cmd = ['python', str(BASE_DIR / 'scripts/create_video.py')]

        if data.get('composer') and data['composer'] != 'random':
            cmd.extend(['--composer', data['composer']])

        cmd.extend(['--duration', str(data.get('duration', 2))])

        if data.get('mood') and data['mood'] != 'random':
            cmd.extend(['--mood', data['mood']])

        if data.get('activity') and data['activity'] != 'random':
            cmd.extend(['--activity', data['activity']])

        if data.get('immersive'):
            cmd.append('--immersive')

        if data.get('ai_titles'):
            cmd.append('--ai-titles')

        if not data.get('auto_upload'):
            cmd.append('--no-upload')

        # Запускаем
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        return jsonify({
            'success': result.returncode == 0,
            'title': f"{data.get('mood', 'melancholic')} {data.get('composer', 'chopin')}",
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/status')
def api_status():
    """API endpoint для статуса"""
    return jsonify(get_library_counts())

if __name__ == '__main__':
    print("🌐 Starting Classical Piano Agent Web Interface")
    print("📱 Open: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)
