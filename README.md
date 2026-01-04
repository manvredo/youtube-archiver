# YouTube Video Archiver with Tor

A Python-based tool for archiving YouTube videos anonymously using Tor, with comprehensive metadata extraction.

## ⚠️ Disclaimer

**This tool is for personal archival and educational purposes only.**

- ✅ Respect YouTube's Terms of Service
- ✅ Only download content you have permission to archive
- ✅ Don't redistribute copyrighted content
- ✅ Use responsibly and ethically
- ✅ Check local laws regarding content downloading

The author is not responsible for misuse of this tool.

## 🎯 Features

- 🔒 **Tor Integration** - Anonymous downloads via SOCKS5 proxy
- 📦 **Batch Processing** - Download videos in manageable portions (default: 10 at a time)
- 🎨 **Metadata Extraction** - Saves thumbnails, descriptions, subtitles, and video info
- 🔄 **Duplicate Detection** - Automatically skips already downloaded videos
- 🚫 **Smart Error Handling** - Handles members-only, private, and unavailable videos
- 📊 **HTML Catalog Generator** - Create searchable video catalog
- 💾 **Resume Support** - Continue interrupted downloads

## 📋 Requirements

- Python 3.7+
- Tor Browser or Tor service
- Windows/Linux/Mac

## 🚀 Installation

1. **Clone the repository:**
```bash
   git clone https://github.com/manvredo/youtube-archiver.git
   cd youtube-archiver
```

2. **Install dependencies:**
```bash
   pip install yt-dlp requests PySocks stem selenium webdriver-manager
```

3. **Install Tor Browser:**
   - Download from: https://www.torproject.org/download/
   - Start Tor Browser (runs on port 9150 by default)

4. **Configure:**
```bash
   copy config.example.json config.json
   notepad config.json
```

## ⚙️ Configuration

Create `config.json`:
```json
{
  "tor_password": "",
  "verbose_logging": false
}
```

## 📖 Usage

### 1. Extract Video Links
```bash
python extract_youtube_links.py
```

- Enter YouTube channel/playlist URL
- Choose how many videos to collect (default: 10)
- Links are saved to `dataset.csv`

### 2. Download Videos
```bash
python downloader.py
```

- Downloads videos from `dataset.csv`
- Saves to `videos/` folder with metadata
- Tracks progress in `completed_downloads.csv`

### 3. Generate Catalog (Optional)
```bash
python create_catalog.py
```

Creates `video_katalog.html` - a searchable catalog of all downloaded videos.

## 📁 Project Structure
```
youtube-archiver/
├── downloader.py              # Main download script
├── extract_youtube_links.py   # Link extraction tool
├── create_catalog.py          # HTML catalog generator
├── config.json               # Configuration (not in repo)
├── dataset.csv               # Video URLs to download (not in repo)
├── completed_downloads.csv   # Download progress (not in repo)
└── videos/                   # Downloaded content (not in repo)
    ├── VIDEO_ID - Title.mp4
    ├── VIDEO_ID - Title.jpg         # Thumbnail
    ├── VIDEO_ID - Title.info.json   # Metadata
    └── VIDEO_ID - Title.description # Description
```

## 🔧 Advanced Features

### Smart Video Categorization

Videos are automatically categorized:
- ✅ `completed_downloads.csv` - Successfully downloaded
- ⚠️ `members_only.csv` - Members-only content (skipped)
- 🔒 `private_videos.csv` - Private videos (skipped)
- ❌ `unavailable_videos.csv` - Unavailable content
- ⚠️ `error_files.csv` - Download errors

### IP Rotation

- New Tor IP for each video download
- Reduces spam detection risk
- Maximizes anonymity

### Metadata Preservation

Each video saves:
- Video file (MP4/WebM)
- Thumbnail (JPG)
- Complete metadata (JSON)
- Description text
- Subtitles (if available, DE/EN)

## 🛡️ Privacy & Security

- ✅ All downloads via Tor network
- ✅ Config and personal data in `.gitignore`
- ✅ No tracking or analytics
- ✅ Local-only operation

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

## ⚡ Troubleshooting

**"Connection refused" error:**
- Ensure Tor Browser is running
- Check port 9150 (Tor Browser) or 9050 (Tor service)

**"Fragment not found" errors:**
- Normal with Tor - retry logic handles this
- Videos download successfully despite warnings

**"Members only" videos:**
- Automatically skipped and logged
- No manual intervention needed

## 📚 Use Cases

- 📺 Personal video archival
- 🎓 Educational content preservation
- 🎨 Art tutorial collections
- 📖 Research material backup
- 🗂️ Offline video libraries

## 🌟 Acknowledgments

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloader
- [Tor Project](https://www.torproject.org/) - Anonymity network
- [Stem](https://stem.torproject.org/) - Tor controller library

---

**Made with ❤️ for preserving digital content**