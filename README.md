[README.md](https://github.com/user-attachments/files/32680109/README.md)
# Multi-Folder Series Batch Renamer

A lightweight, high-performance GUI tool designed for media collectors to effortlessly batch-rename TV series, anime, and subtitles across multiple folders. Perfectly structured for seamless **Jellyfin**, **Emby**, and **Plex** metadata scraping.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

---

## 🌟 Key Features

- **📂 Multi-Folder & Sub-scan**: Import multiple show folders simultaneously or auto-scan all sub-series under a root directory with one click.
- **🎬 Jellyfin/Plex Ready**: Standardizes naming formats (e.g., `Show Name - S01E01 - [1080p].mkv`) to ensure perfect compatibility with media server scrapers.
- **📝 Smart Subtitle Pairing**: Automatically detects video and subtitle files (`.srt`, `.ass`, etc.), matching them to the correct episode numbers.
- **🔍 Smart Show Name Deduction**: Intelligently extracts clean show titles by stripping out messy release tags, resolutions, and brackets.
- **⚡ Real-Time Preview & Inline Editing**: Instantly preview rename results and tweak individual file names, season numbers, or start episodes on the fly.
- **🛡️ Conflict Prevention**: Built-in duplicate detection and safety warnings to prevent file overwriting accidents.
- **🌍 Multi-Language GUI**: Supports Traditional Chinese (繁體中文), Simplified Chinese (简体中文), English, Japanese (日本語), and Korean (한국어) with Dark/Light mode support.

---

## 🚀 Quick Start (For Users)

If you just want to use the tool without dealing with Python:
1. Head over to the **[Releases](../../releases)** page.
2. Download the latest compiled `.exe` file (`SeriesRenamer.exe`).
3. Double-click to run and start organizing your media library instantly!

---

## 💻 Running from Source (For Developers)

If you prefer to run or modify the Python script directly:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/你的帳號名稱/multi-folder-series-renamer.git](https://github.com/你的帳號名稱/multi-folder-series-renamer.git)
   cd multi-folder-series-renamer
