#!/usr/bin/env python3
"""
Mandarin Learning Tool
Converts Chinese text to Pinyin with Dutch translations
Generates beautiful HTML output for optimal learning experience
"""

import os
import sys
import re
import json
import html
from datetime import datetime
from typing import List, Tuple, Dict, Optional

try:
    from pypinyin import pinyin, Style
    import jieba
    from deep_translator import GoogleTranslator
except ImportError:
    print("Missing dependencies. Please install them with:")
    print("pip install -r requirements.txt")
    sys.exit(1)

from hsk_data import (
    get_hsk_level, 
    get_character_breakdown, 
    get_hsk_color, 
    get_frequency_label,
    CHARACTER_MEANINGS
)

# Cache for translations to avoid repeated API calls
TRANSLATION_CACHE_FILE = "translation_cache.json"

def load_translation_cache() -> Dict[str, str]:
    """Load cached translations from file"""
    if os.path.exists(TRANSLATION_CACHE_FILE):
        try:
            with open(TRANSLATION_CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_translation_cache(cache: Dict[str, str]):
    """Save translations to cache file"""
    try:
        with open(TRANSLATION_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except IOError as e:
        print(f"Warning: Could not save translation cache: {e}")

def get_pinyin(text: str) -> str:
    """Convert Chinese text to pinyin with tone marks"""
    result = pinyin(text, style=Style.TONE)
    return ''.join([p[0] for p in result])

def segment_text(text: str) -> List[str]:
    """Segment Chinese text into words using jieba"""
    # Use jieba for word segmentation
    words = list(jieba.cut(text))
    return words

def translate_word(word: str, cache: Dict[str, str], translator: GoogleTranslator) -> str:
    """Translate a Chinese word to Dutch"""
    # Skip punctuation and whitespace
    if not word.strip() or all(c in '。，！？、；：""''（）【】《》…—' for c in word):
        return word
    
    # Check cache first
    if word in cache:
        return cache[word]
    
    try:
        translation = translator.translate(word)
        cache[word] = translation
        return translation
    except Exception as e:
        print(f"Warning: Could not translate '{word}': {e}")
        return "?"

def is_chinese(text: str) -> bool:
    """Check if text contains Chinese characters"""
    for char in text:
        if '\u4e00' <= char <= '\u9fff':
            return True
    return False

def process_text(chinese_text: str) -> List[Dict]:
    """Process Chinese text and return structured data for each word"""
    # Initialize translator
    translator = GoogleTranslator(source='zh-CN', target='nl')
    
    # Load translation cache
    cache = load_translation_cache()
    
    # Segment the text
    words = segment_text(chinese_text)
    
    results = []
    for word in words:
        word = word.strip()
        if not word:
            continue
            
        # Check if it's Chinese
        if is_chinese(word):
            word_pinyin = get_pinyin(word)
            dutch_translation = translate_word(word, cache, translator)
            hsk_level, frequency = get_hsk_level(word)
            breakdown = get_character_breakdown(word)
            
            results.append({
                'chinese': word,
                'pinyin': word_pinyin,
                'dutch': dutch_translation,
                'hsk_level': hsk_level,
                'frequency': frequency,
                'breakdown': breakdown,
                'is_chinese': True
            })
        else:
            # Non-Chinese text (punctuation, numbers, etc.)
            results.append({
                'chinese': word,
                'pinyin': word,
                'dutch': word,
                'hsk_level': 0,
                'frequency': 0,
                'breakdown': None,
                'is_chinese': False
            })
    
    # Save updated cache
    save_translation_cache(cache)
    
    return results

def generate_html(results: List[Dict], original_text: str, dutch_full_text: str = "", dark_mode: bool = False) -> str:
    """Generate beautiful HTML output"""
    
    # Determine theme colors
    if dark_mode:
        bg_color = "#1a1a2e"
        text_color = "#eaeaea"
        card_bg = "#16213e"
        border_color = "#0f3460"
        pinyin_color = "#00d9ff"
        dutch_color = "#ffd700"
        hover_bg = "#0f3460"
    else:
        bg_color = "#f5f7fa"
        text_color = "#2c3e50"
        card_bg = "#ffffff"
        border_color = "#e1e8ed"
        pinyin_color = "#3498db"
        dutch_color = "#e67e22"
        hover_bg = "#f8f9fa"
    
    html_content = f'''<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mandarijn Leren - {datetime.now().strftime("%Y-%m-%d %H:%M")}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: {bg_color};
            --text-color: {text_color};
            --card-bg: {card_bg};
            --border-color: {border_color};
            --pinyin-color: {pinyin_color};
            --dutch-color: {dutch_color};
            --hover-bg: {hover_bg};
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', 'Noto Sans SC', sans-serif;
            background: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .subtitle {{
            color: #888;
            font-size: 0.9rem;
        }}
        
        .controls {{
            display: flex;
            gap: 10px;
            justify-content: center;
            margin-top: 15px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .btn-primary {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .btn-secondary {{
            background: var(--border-color);
            color: var(--text-color);
        }}
        
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }}
        
        .legend {{
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
            margin: 20px 0;
            padding: 15px;
            background: var(--card-bg);
            border-radius: 12px;
        }}
        
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 5px;
            font-size: 0.8rem;
        }}
        
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        
        .original-text {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }}
        
        .original-text h3 {{
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 10px;
        }}
        
        .original-text p {{
            font-size: 1.2rem;
            font-family: 'Noto Sans SC', sans-serif;
        }}
        
        .dutch-translation {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            border-left: 4px solid #FF9800;
        }}
        
        .dutch-translation h3 {{
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 10px;
        }}
        
        .dutch-translation p {{
            font-size: 1.1rem;
            line-height: 1.8;
            color: var(--dutch-color);
        }}
        
        .dutch-translation em {{
            color: #888;
            font-style: italic;
        }}
        
        .word-grid {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            padding: 20px;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .word-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px 16px;
            background: var(--hover-bg);
            border-radius: 12px;
            border: 2px solid transparent;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            min-width: 80px;
        }}
        
        .word-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            border-color: var(--pinyin-color);
        }}
        
        .word-card.punctuation {{
            min-width: auto;
            padding: 12px 8px;
            background: transparent;
        }}
        
        .word-card.punctuation:hover {{
            transform: none;
            box-shadow: none;
            border-color: transparent;
        }}
        
        .chinese {{
            font-size: 1.8rem;
            font-family: 'Noto Sans SC', sans-serif;
            font-weight: 500;
            margin-bottom: 4px;
        }}
        
        .pinyin {{
            font-size: 1rem;
            color: var(--pinyin-color);
            font-weight: 500;
            margin-bottom: 2px;
        }}
        
        .dutch {{
            font-size: 0.85rem;
            color: var(--dutch-color);
            font-weight: 500;
            text-align: center;
            max-width: 120px;
            word-wrap: break-word;
        }}
        
        .hsk-badge {{
            position: absolute;
            top: -8px;
            right: -8px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            font-weight: bold;
            color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }}
        
        .tooltip {{
            display: none;
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: #2c3e50;
            color: white;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
            margin-bottom: 10px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}
        
        .tooltip::after {{
            content: '';
            position: absolute;
            top: 100%;
            left: 50%;
            transform: translateX(-50%);
            border: 8px solid transparent;
            border-top-color: #2c3e50;
        }}
        
        .word-card:hover .tooltip {{
            display: block;
        }}
        
        .tooltip-row {{
            display: flex;
            gap: 10px;
            margin-bottom: 4px;
        }}
        
        .tooltip-label {{
            color: #95a5a6;
        }}
        
        .breakdown {{
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #34495e;
        }}
        
        .breakdown-char {{
            display: inline-block;
            margin-right: 8px;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        
        .stat-card {{
            background: var(--card-bg);
            padding: 15px;
            border-radius: 12px;
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 1.5rem;
            font-weight: bold;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        .stat-label {{
            font-size: 0.8rem;
            color: #888;
            margin-top: 5px;
        }}
        
        .vocabulary-list {{
            margin-top: 30px;
            background: var(--card-bg);
            border-radius: 16px;
            padding: 20px;
        }}
        
        .vocabulary-list h2 {{
            margin-bottom: 15px;
            font-size: 1.2rem;
        }}
        
        .vocab-table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .vocab-table th,
        .vocab-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .vocab-table th {{
            font-weight: 600;
            color: #888;
            font-size: 0.85rem;
        }}
        
        .vocab-table tr:hover {{
            background: var(--hover-bg);
        }}
        
        .copy-btn, .audio-btn {{
            background: none;
            border: none;
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            transition: background 0.2s;
        }}
        
        .copy-btn:hover, .audio-btn:hover {{
            background: var(--border-color);
        }}
        
        .audio-btn {{
            font-size: 1.1rem;
        }}
        
        .audio-btn:active {{
            transform: scale(0.95);
        }}
        
        .audio-btn.playing {{
            animation: pulse 0.5s ease-in-out infinite;
        }}
        
        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.5; }}
        }}
        
        .word-audio-btn {{
            position: absolute;
            top: -8px;
            left: -8px;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
        }}
        
        .word-audio-btn:hover {{
            background: #764ba2;
            transform: scale(1.1);
        }}
        
        .word-audio-btn:active {{
            transform: scale(0.95);
        }}
        
        .notification {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #2ecc71;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            display: none;
            animation: slideIn 0.3s ease;
        }}
        
        @keyframes slideIn {{
            from {{
                transform: translateX(100%);
                opacity: 0;
            }}
            to {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
        
        footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            color: #888;
            font-size: 0.85rem;
        }}
        
        @media (max-width: 768px) {{
            .word-card {{
                min-width: 70px;
                padding: 10px 12px;
            }}
            
            .chinese {{
                font-size: 1.5rem;
            }}
            
            .pinyin {{
                font-size: 0.9rem;
            }}
            
            .dutch {{
                font-size: 0.75rem;
            }}
        }}
        
        /* Print styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            
            .controls, .btn {{
                display: none;
            }}
            
            .word-card {{
                break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🇨🇳 Mandarijn Leren 🇳🇱</h1>
            <p class="subtitle">Chinese tekst met Pinyin en Nederlandse vertaling</p>
            <div class="controls">
                <button class="btn btn-primary" onclick="toggleDarkMode()">
                    🌙 Donkere modus
                </button>
                <button class="btn btn-secondary" onclick="window.print()">
                    🖨️ Afdrukken
                </button>
                <button class="btn btn-secondary" onclick="copyAllVocab()">
                    📋 Kopieer woordenlijst
                </button>
            </div>
        </header>
        
        <div class="legend">
            <div class="legend-item">
                <span class="legend-dot" style="background: #4CAF50;"></span>
                <span>HSK 1 (Beginner)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #8BC34A;"></span>
                <span>HSK 2 (Elementair)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #FFC107;"></span>
                <span>HSK 3 (Gemiddeld)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #FF9800;"></span>
                <span>HSK 4 (Bovengemiddeld)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #FF5722;"></span>
                <span>HSK 5 (Gevorderd)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #F44336;"></span>
                <span>HSK 6 (Meesterschap)</span>
            </div>
            <div class="legend-item">
                <span class="legend-dot" style="background: #9E9E9E;"></span>
                <span>Onbekend niveau</span>
            </div>
        </div>
        
        <div class="original-text">
            <h3>📝 Originele tekst (Chinees)</h3>
            <p>{html.escape(original_text)}</p>
        </div>
        
        <div class="dutch-translation">
            <h3>🇳🇱 Nederlandse vertaling</h3>
            <p>{html.escape(dutch_full_text) if dutch_full_text else '<em>Geen vertaling beschikbaar. Maak een input_dutch.txt bestand aan met de Nederlandse vertaling.</em>'}</p>
        </div>
        
        <div class="word-grid">
'''
    
    # Generate word cards
    for item in results:
        if not item['is_chinese']:
            # Punctuation or non-Chinese
            html_content += f'''
            <div class="word-card punctuation">
                <span class="chinese">{html.escape(item['chinese'])}</span>
            </div>
'''
        else:
            hsk_color = get_hsk_color(item['hsk_level'])
            freq_label = get_frequency_label(item['frequency'])
            
            # Build breakdown HTML
            breakdown_html = ""
            if item['breakdown']:
                breakdown_html = '<div class="breakdown"><strong>Karakters:</strong><br>'
                for char, meaning in item['breakdown']:
                    breakdown_html += f'<span class="breakdown-char">{html.escape(char)} = {html.escape(meaning)}</span>'
                breakdown_html += '</div>'
            
            hsk_display = f"HSK {item['hsk_level']}" if item['hsk_level'] > 0 else "Onbekend"
            
            html_content += f'''
            <div class="word-card" onclick="copyWord('{html.escape(item['chinese'])}')">
                <div class="tooltip">
                    <div class="tooltip-row">
                        <span class="tooltip-label">Niveau:</span>
                        <span>{hsk_display}</span>
                    </div>
                    <div class="tooltip-row">
                        <span class="tooltip-label">Frequentie:</span>
                        <span>{freq_label}</span>
                    </div>
                    {breakdown_html}
                    <div style="margin-top: 8px; font-size: 0.7rem; color: #95a5a6;">
                        Klik om te kopiëren | 🔊 voor audio
                    </div>
                </div>
                <button class="word-audio-btn" onclick="event.stopPropagation(); speakChinese('{html.escape(item['chinese'])}', this)" title="Uitspraak beluisteren">🔊</button>
                <span class="hsk-badge" style="background: {hsk_color};">
                    {item['hsk_level'] if item['hsk_level'] > 0 else '?'}
                </span>
                <span class="chinese">{html.escape(item['chinese'])}</span>
                <span class="pinyin">{html.escape(item['pinyin'])}</span>
                <span class="dutch">{html.escape(item['dutch'])}</span>
            </div>
'''
    
    html_content += '''
        </div>
'''
    
    # Calculate statistics
    chinese_words = [r for r in results if r['is_chinese']]
    unique_words = list({r['chinese']: r for r in chinese_words}.values())
    hsk_counts = {}
    for word in unique_words:
        level = word['hsk_level']
        hsk_counts[level] = hsk_counts.get(level, 0) + 1
    
    html_content += f'''
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(chinese_words)}</div>
                <div class="stat-label">Totaal woorden</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(unique_words)}</div>
                <div class="stat-label">Unieke woorden</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(len(r['chinese']) for r in chinese_words)}</div>
                <div class="stat-label">Totaal karakters</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{hsk_counts.get(1, 0) + hsk_counts.get(2, 0)}</div>
                <div class="stat-label">HSK 1-2 woorden</div>
            </div>
        </div>
        
        <div class="vocabulary-list">
            <h2>📚 Woordenlijst</h2>
            <table class="vocab-table">
                <thead>
                    <tr>
                        <th>Chinees</th>
                        <th>Pinyin</th>
                        <th>Nederlands</th>
                        <th>HSK</th>
                        <th>Audio</th>
                        <th>Kopiëren</th>
                    </tr>
                </thead>
                <tbody>
'''
    
    # Add vocabulary table rows (unique words only)
    for word in unique_words:
        hsk_display = f"HSK {word['hsk_level']}" if word['hsk_level'] > 0 else "-"
        hsk_color = get_hsk_color(word['hsk_level'])
        html_content += f'''
                    <tr>
                        <td style="font-family: 'Noto Sans SC', sans-serif; font-size: 1.2rem;">{html.escape(word['chinese'])}</td>
                        <td style="color: var(--pinyin-color);">{html.escape(word['pinyin'])}</td>
                        <td style="color: var(--dutch-color);">{html.escape(word['dutch'])}</td>
                        <td><span style="color: {hsk_color}; font-weight: bold;">{hsk_display}</span></td>
                        <td>
                            <button class="audio-btn" onclick="speakChinese('{html.escape(word['chinese'])}', this)" title="Uitspraak beluisteren">🔊</button>
                        </td>
                        <td>
                            <button class="copy-btn" onclick="copyWord('{html.escape(word['chinese'])}')">📋</button>
                        </td>
                    </tr>
'''
    
    html_content += '''
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Gegenereerd op ''' + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '''</p>
            <p>💡 Tip: Klik op 🔊 voor uitspraak, klik op een woord om te kopiëren. Hover voor meer informatie.</p>
        </footer>
    </div>
    
    <div class="notification" id="notification">
        ✓ Gekopieerd naar klembord!
    </div>
    
    <script>
        // Text-to-Speech for Chinese pronunciation
        let currentUtterance = null;
        
        function speakChinese(text, button) {
            // Cancel any ongoing speech
            if (window.speechSynthesis.speaking) {
                window.speechSynthesis.cancel();
            }
            
            // Check if Web Speech API is supported
            if (!('speechSynthesis' in window)) {
                alert('Je browser ondersteunt geen spraaksynthese. Probeer Chrome, Edge of Safari.');
                return;
            }
            
            // Create utterance
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'zh-CN';
            utterance.rate = 0.8;  // Slightly slower for learning
            utterance.pitch = 1;
            utterance.volume = 1;
            
            // Try to find a Chinese voice
            const voices = window.speechSynthesis.getVoices();
            const chineseVoice = voices.find(voice =>
                voice.lang.includes('zh') ||
                voice.lang.includes('cmn') ||
                voice.name.toLowerCase().includes('chinese')
            );
            
            if (chineseVoice) {
                utterance.voice = chineseVoice;
            }
            
            // Visual feedback
            if (button) {
                button.classList.add('playing');
            }
            
            utterance.onend = () => {
                if (button) {
                    button.classList.remove('playing');
                }
            };
            
            utterance.onerror = (event) => {
                if (button) {
                    button.classList.remove('playing');
                }
                console.error('Speech synthesis error:', event.error);
            };
            
            // Speak
            window.speechSynthesis.speak(utterance);
        }
        
        // Load voices (needed for some browsers)
        if ('speechSynthesis' in window) {
            window.speechSynthesis.onvoiceschanged = () => {
                window.speechSynthesis.getVoices();
            };
        }
        
        function copyWord(text) {
            navigator.clipboard.writeText(text).then(() => {
                showNotification();
            });
        }
        
        function showNotification() {
            const notification = document.getElementById('notification');
            notification.style.display = 'block';
            setTimeout(() => {
                notification.style.display = 'none';
            }, 2000);
        }
        
        function toggleDarkMode() {
            document.body.classList.toggle('dark-mode');
            const isDark = document.body.classList.contains('dark-mode');
            
            if (isDark) {
                document.documentElement.style.setProperty('--bg-color', '#1a1a2e');
                document.documentElement.style.setProperty('--text-color', '#eaeaea');
                document.documentElement.style.setProperty('--card-bg', '#16213e');
                document.documentElement.style.setProperty('--border-color', '#0f3460');
                document.documentElement.style.setProperty('--hover-bg', '#0f3460');
            } else {
                document.documentElement.style.setProperty('--bg-color', '#f5f7fa');
                document.documentElement.style.setProperty('--text-color', '#2c3e50');
                document.documentElement.style.setProperty('--card-bg', '#ffffff');
                document.documentElement.style.setProperty('--border-color', '#e1e8ed');
                document.documentElement.style.setProperty('--hover-bg', '#f8f9fa');
            }
        }
        
        function copyAllVocab() {
            const rows = document.querySelectorAll('.vocab-table tbody tr');
            let text = 'Chinees\\tPinyin\\tNederlands\\tHSK\\n';
            rows.forEach(row => {
                const cells = row.querySelectorAll('td');
                text += `${cells[0].textContent}\\t${cells[1].textContent}\\t${cells[2].textContent}\\t${cells[3].textContent}\\n`;
            });
            navigator.clipboard.writeText(text).then(() => {
                showNotification();
            });
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                toggleDarkMode();
            }
            if (e.ctrlKey && e.key === 'p') {
                e.preventDefault();
                window.print();
            }
        });
    </script>
</body>
</html>
'''
    
    return html_content

def main():
    """Main function"""
    input_file = "input.txt"
    input_dutch_file = "input_dutch.txt"
    output_file = "output.html"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        # Create a sample input file
        sample_text = """你好，我叫小明。我是中国人。我喜欢学习汉语。
今天天气很好。我想去公园散步。
你喜欢吃什么？我喜欢吃米饭和蔬菜。"""
        
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write(sample_text)
        
        print(f"📝 Voorbeeld bestand '{input_file}' aangemaakt.")
        print(f"   Bewerk dit bestand met je Chinese tekst en voer het script opnieuw uit.")
        print()
    
    # Read input file
    print(f"📖 Lezen van '{input_file}'...")
    with open(input_file, 'r', encoding='utf-8') as f:
        chinese_text = f.read().strip()
    
    if not chinese_text:
        print("❌ Het invoerbestand is leeg. Voeg Chinese tekst toe aan input.txt")
        sys.exit(1)
    
    # Read Dutch translation file (optional)
    dutch_full_text = ""
    if os.path.exists(input_dutch_file):
        print(f"📖 Lezen van '{input_dutch_file}'...")
        with open(input_dutch_file, 'r', encoding='utf-8') as f:
            dutch_full_text = f.read().strip()
        if dutch_full_text:
            print(f"   ✓ Nederlandse vertaling geladen ({len(dutch_full_text)} karakters)")
    else:
        print(f"ℹ️  Geen '{input_dutch_file}' gevonden. Maak dit bestand aan voor de volledige Nederlandse vertaling.")
        # Create empty sample file
        with open(input_dutch_file, 'w', encoding='utf-8') as f:
            f.write("# Voeg hier de Nederlandse vertaling van de Chinese tekst toe\n")
        print(f"   📝 Leeg bestand '{input_dutch_file}' aangemaakt.")
    
    print(f"� Verwerken van {len(chinese_text)} karakters...")
    print()
    
    # Process the text
    results = process_text(chinese_text)
    
    # Generate HTML
    print("🎨 HTML genereren...")
    html_output = generate_html(results, chinese_text, dutch_full_text)
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Uitvoer opgeslagen naar '{output_file}'")
    print()
    
    # Print summary to terminal
    chinese_words = [r for r in results if r['is_chinese']]
    unique_words = list({r['chinese']: r for r in chinese_words}.values())
    
    print("=" * 60)
    print("📊 SAMENVATTING")
    print("=" * 60)
    print(f"   Totaal woorden: {len(chinese_words)}")
    print(f"   Unieke woorden: {len(unique_words)}")
    print(f"   Totaal karakters: {sum(len(r['chinese']) for r in chinese_words)}")
    print()
    
    # Print first few words as preview
    print("📝 VOORBEELD (eerste 10 woorden):")
    print("-" * 60)
    for i, word in enumerate(unique_words[:10]):
        hsk = f"HSK{word['hsk_level']}" if word['hsk_level'] > 0 else "?"
        print(f"   {word['chinese']} | {word['pinyin']} | {word['dutch']} | {hsk}")
    
    if len(unique_words) > 10:
        print(f"   ... en {len(unique_words) - 10} meer woorden")
    
    print()
    print(f"🌐 Open '{output_file}' in je browser voor de volledige interactieve weergave!")
    print()

if __name__ == "__main__":
    main()
