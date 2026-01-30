# Mandarin Learning Tool

Convert Chinese text into **Pinyin** with **Dutch translations**, enrich the output with **HSK levels**, and generate a **beautiful, interactive HTML learning sheet**.

This project consists of three files:

- `mandarin_converter.py`
- `hsk_data.py`
- `requirements.txt`

## ✨ Features
- Chinese → Pinyin with tone marks
- Word segmentation using jieba
- Dutch translation using deep-translator + caching
- HSK level + frequency lookup
- Character breakdown tooltips
- Interactive HTML UI (dark mode, copy buttons, statistics, vocabulary list)

## 📁 Repository Structure
```
.
├── mandarin_converter.py
├── hsk_data.py
└── requirements.txt
```

## 🚀 Installation
If you don't have venv set up yet:
```bash
python3 -m venv .venv
```

Open venv environment
```bash
source .venv/bin/activate
```

```bash
Install dependencies if not done before:
pip install -r requirements.txt
```

## ▶️ Usage
```bash
python mandarin_converter.py
```
If no `input.txt` exists, the program creates one. Edit it with Chinese text and run again. `output.html` will be created.

## 🧠 How It Works
- Segmentation via jieba
- Pinyin via pypinyin
- Dutch translation via GoogleTranslator
- HSK lookup + frequency ranking
- Character-level decomposition
- HTML template generation

## 📊 Output
- Word cards with Chinese, Pinyin, Dutch
- Tooltips (HSK level, meaning breakdown)
- Vocabulary table
- Statistics section

## 🛠 Customization
- Change translation language
- Adjust input/output filenames
- Expand HSK vocabulary
- Edit CSS theme variables

## ❗ Troubleshooting
- Ensure dependencies installed
- Translation failures show `?`
- Segmentation may vary due to jieba

## 🔒 Privacy
Uses online translation API.

## 📄 License
Add your license here.
