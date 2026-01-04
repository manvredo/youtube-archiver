import yt_dlp
import requests
import csv
from stem import Signal
from stem.control import Controller
import os
import sys
import json
import re

def extract_video_id(url):
    """Extrahiert die Video-ID aus verschiedenen YouTube-URL-Formaten"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url.strip()):
        return url.strip()
    
    return None

def is_video_downloaded(video_id, videos_folder='videos'):
    """Prüft ob Video bereits heruntergeladen wurde"""
    if not os.path.exists(videos_folder):
        return False
    
    for filename in os.listdir(videos_folder):
        if filename.startswith(video_id):
            return True
    return False

def renew_connection(tor_password):
    with Controller.from_port(port = 9151) as controller:
        controller.authenticate(password=tor_password)
        controller.signal(Signal.NEWNYM)

def download_video(config, video_url_or_id):
    videoId = extract_video_id(video_url_or_id)
    
    if not videoId:
        print(f'Konnte keine Video-ID extrahieren aus: {video_url_or_id}')
        return False
    
    if is_video_downloaded(videoId):
        print(f'Video {videoId} wurde bereits heruntergeladen (im videos/ Ordner gefunden)')
        return True
    
    ydl_opts = {
        'outtmpl': os.path.dirname(os.path.realpath(__file__)) + '/videos/' + '%(id)s - %(title)s.%(ext)s',
        'proxy': 'socks5://127.0.0.1:9150',
        'verbose': config['verbose_logging'],
        'nocheckcertificate': True,
        'retries': 10,
        'fragment_retries': 10,
        'skip_unavailable_fragments': True,
        'ignoreerrors': True,
        'socket_timeout': 30,
        'http_chunk_size': 10485760,
        'writethumbnail': True,
        'writeinfojson': True,
        'writedescription': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['de', 'en'],
        'restrictfilenames': False,
        'windowsfilenames': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Erst Info holen ohne Download
            info = ydl.extract_info(f'http://www.youtube.com/watch?v={videoId}', download=False)
            
            # Prüfe Verfügbarkeit
            availability = info.get('availability', '')
            if availability in ['subscriber_only', 'premium_only', 'needs_auth']:
                print(f'⚠️  Video {videoId} ist nur für Mitglieder/Premium - übersprungen')
                with open('members_only.csv', 'a', encoding='utf-8') as f:
                    f.write(video_url_or_id + '\n')
                return False
            
            # Jetzt downloaden
            ydl.params['download'] = True
            ydl.download([f'http://www.youtube.com/watch?v={videoId}'])
            return True
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Kategorisiere Fehler
        if any(keyword in error_msg for keyword in ['members only', 'join this channel', 'subscriber', 'members-only', 'premium']):
            print(f'⚠️  Video {videoId} nur für Mitglieder - in members_only.csv gespeichert')
            with open('members_only.csv', 'a', encoding='utf-8') as f:
                f.write(video_url_or_id + '\n')
            return False
        elif 'private' in error_msg:
            print(f'⚠️  Video {videoId} ist privat - in private_videos.csv gespeichert')
            with open('private_videos.csv', 'a', encoding='utf-8') as f:
                f.write(video_url_or_id + '\n')
            return False
        elif 'unavailable' in error_msg or 'video unavailable' in error_msg:
            print(f'⚠️  Video {videoId} ist nicht verfügbar - in unavailable_videos.csv gespeichert')
            with open('unavailable_videos.csv', 'a', encoding='utf-8') as f:
                f.write(video_url_or_id + '\n')
            return False
        else:
            print(f'❌ Unbekannter Fehler bei {videoId}: {e}')
            return False

def test_proxy(config):
    print('----------------------------------------------')
    print('Running Proxy Test')
    print('Your IP:')
    ip_test = requests.get('http://httpbin.org/ip').json()
    print(requests.get('http://httpbin.org/ip').json())
    
    try:
        renew_connection(config['tor_password'])
    except:
        print('Warning: Could not renew Tor connection (Controller Port not available)')
    
    print('Tor IP:')
    tor_ip_test = requests.Session().get('http://httpbin.org/ip', proxies={ 
        'http': 'socks5://127.0.0.1:9150',
        'https': 'socks5://127.0.0.1:9150'
    }).json()
    print(tor_ip_test)
    
    test_result = False
    if ip_test != tor_ip_test:
        print('Tor IP working correctly')
        test_result = True
    else:
        print('Your IP and Tor IP are the same: check you are running Tor Browser')
    
    return test_result

completed_downloads = []
videos_to_download = []

config_file = open('config.json', 'r')
config = json.load(config_file)

if not os.path.exists('videos'):
    os.makedirs('videos')

video_dataset_file = open('dataset.csv', 'r', encoding='utf-8')
video_dataset = video_dataset_file.read().splitlines()
video_dataset_file.close()
print(f'{ len(video_dataset) } \tYouTube Videos in dataset')

if not os.path.exists('completed_downloads.csv'):
    open('completed_downloads.csv', 'w').close()

completed_downloads_file = open('completed_downloads.csv', 'r', encoding='utf-8')
completed_downloads = completed_downloads_file.read().splitlines()
completed_downloads_file.close()
print(f'{ len(completed_downloads) } \tCompleted downloads')

# Prüfe auch videos/ Ordner
already_downloaded = []
for video in video_dataset:
    video_id = extract_video_id(video)
    if video_id and is_video_downloaded(video_id):
        already_downloaded.append(video)

print(f'{ len(already_downloaded) } \tBereits im videos/ Ordner')

# Exclude completed downloads AND already downloaded videos
videos_to_download = list(set(video_dataset) - set(completed_downloads) - set(already_downloaded))
print(f'{ len(videos_to_download) } \tVideos to download')

if len(videos_to_download) == 0:
    print('No videos to download!')
    sys.exit()

if test_proxy(config) == False:
    sys.exit()

successful_downloads = 0
skipped_videos = 0

for video in videos_to_download:
    print(f'\n----------------------------------------------')
    print(f'Processing: {video}')
    print('New Tor IP Address Allocated')
    try:
        renew_connection(config['tor_password'])
    except:
        print('Warning: Could not renew Tor connection')
    
    try:
        result = download_video(config, video)
        
        if result == True:
            # Erfolgreich heruntergeladen
            videos_to_download.remove(video)
            completed_downloads.append(video)
            with open('completed_downloads.csv', 'a', encoding='utf-8') as f:
                f.write(video)
                f.write('\n')
            print(f'✓ Successfully downloaded: {video}')
            successful_downloads += 1
        else:
            # Übersprungen (Members-only, Private, etc.)
            videos_to_download.remove(video)
            print(f'⊘ Skipped: {video}')
            skipped_videos += 1
            
    except Exception as e:
        print(f'❌ Error downloading file: {video}')
        print(f'Error message: {str(e)}')
        with open('error_files.csv', 'a', encoding='utf-8') as f:
            f.write(video)
            f.write('\n')

print('')
print('=' * 60)
print('DOWNLOAD STATISTIK')
print('=' * 60)
print(f'✓ Erfolgreich heruntergeladen: {successful_downloads}')
print(f'⊘ Übersprungen:                {skipped_videos}')
print(f'✓ Gesamt in completed_downloads: {len(completed_downloads)}')
print(f'📊 Fortschritt: {len(completed_downloads)}/{len(video_dataset)} ({(len(completed_downloads) / len(video_dataset) * 100):.1f}%)')
print('=' * 60)

# Zeige Zusammenfassung der übersprungenen Videos
if os.path.exists('members_only.csv'):
    with open('members_only.csv', 'r', encoding='utf-8') as f:
        members_count = len(f.read().splitlines())
    if members_count > 0:
        print(f'ℹ️  {members_count} Members-only Videos in members_only.csv')

if os.path.exists('private_videos.csv'):
    with open('private_videos.csv', 'r', encoding='utf-8') as f:
        private_count = len(f.read().splitlines())
    if private_count > 0:
        print(f'ℹ️  {private_count} Private Videos in private_videos.csv')

if os.path.exists('unavailable_videos.csv'):
    with open('unavailable_videos.csv', 'r', encoding='utf-8') as f:
        unavailable_count = len(f.read().splitlines())
    if unavailable_count > 0:
        print(f'ℹ️  {unavailable_count} Nicht verfügbare Videos in unavailable_videos.csv')
```

**Neue Features:**

✅ **Überspringt automatisch:**
- Members-only Videos → `members_only.csv`
- Private Videos → `private_videos.csv`
- Nicht verfügbare Videos → `unavailable_videos.csv`

✅ **Script läuft durch ohne Abbruch**

✅ **Bessere Statistik am Ende:**
```
==========================================================
DOWNLOAD STATISTIK
==========================================================
✓ Erfolgreich heruntergeladen: 8
⊘ Übersprungen:                2
✓ Gesamt in completed_downloads: 8
📊 Fortschritt: 8/10 (80.0%)
==========================================================
ℹ️  2 Members-only Videos in members_only.csv