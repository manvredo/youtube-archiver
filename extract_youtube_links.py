from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import os

def setup_tor_browser():
    """Konfiguriert Chrome/Firefox für Tor"""
    
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=socks5://127.0.0.1:9150')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def extract_video_id(url):
    """Extrahiert Video-ID aus URL"""
    patterns = [
        r'youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_downloaded_video_ids(videos_folder='videos'):
    """Liest Video-IDs aus bereits heruntergeladenen Dateien"""
    video_ids = set()
    
    if not os.path.exists(videos_folder):
        return video_ids
    
    for filename in os.listdir(videos_folder):
        # Extrahiere Video-ID aus Dateinamen (Format: VIDEO_ID.ext)
        video_id = filename.split('.')[0]
        if len(video_id) == 11:  # YouTube Video-IDs sind 11 Zeichen lang
            video_ids.add(video_id)
    
    return video_ids

def extract_youtube_links(url, num_videos=10):
    """Extrahiert die ersten N YouTube-Video-Links von einer Seite über Tor"""
    
    print('Starte Browser mit Tor-Verbindung...')
    driver = setup_tor_browser()
    
    try:
        print('Prüfe Tor-Verbindung...')
        driver.get('http://httpbin.org/ip')
        time.sleep(2)
        ip_info = driver.find_element(By.TAG_NAME, 'body').text
        print(f'Aktuelle IP: {ip_info}')
        
        print(f'\nÖffne YouTube-Seite: {url}')
        driver.get(url)
        
        print('Warte auf Seitenladung...')
        time.sleep(5)
        
        print(f'\nSammle {num_videos} Video-Links...')
        links = set()
        scroll_count = 0
        max_scroll_attempts = 20
        
        patterns = [
            r'youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})',
            r'youtu\.be\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})'
        ]
        
        while len(links) < num_videos and scroll_count < max_scroll_attempts:
            elements = driver.find_elements(By.TAG_NAME, 'a')
            
            for element in elements:
                try:
                    href = element.get_attribute('href')
                    if href:
                        for pattern in patterns:
                            match = re.search(pattern, href)
                            if match:
                                clean_url = href.split('&')[0].split('#')[0]
                                links.add(clean_url)
                                if len(links) >= num_videos:
                                    break
                        if len(links) >= num_videos:
                            break
                except:
                    continue
            
            if len(links) >= num_videos:
                break
            
            scroll_count += 1
            print(f'  Scroll {scroll_count}, gefunden: {len(links)}/{num_videos}')
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
        
        result_links = sorted(list(links))[:num_videos]
        print(f'\n✓ {len(result_links)} Video-Links gesammelt')
        return result_links
        
    except Exception as e:
        print(f'\nFehler: {e}')
        return []
        
    finally:
        print('\nSchließe Browser...')
        driver.quit()

def save_to_file(links, filename='dataset.csv', mode='w'):
    """Speichert Links in Datei"""
    with open(filename, mode, encoding='utf-8') as f:
        for link in links:
            f.write(link + '\n')
    print(f'✓ {len(links)} Links gespeichert in: {filename}')

def load_existing_links(filename='dataset.csv'):
    """Lädt bereits vorhandene Links"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return set(f.read().splitlines())
    except FileNotFoundError:
        return set()

# Hauptprogramm
if __name__ == '__main__':
    print('=' * 60)
    print('YouTube Link Extraktor (über Tor) - Portionsweise')
    print('=' * 60)
    
    print('\n⚠️  WICHTIG: Stelle sicher, dass Tor Browser läuft!')
    input('Drücke Enter wenn Tor Browser gestartet ist...')
    
    print('\nBeispiele für URLs:')
    print('  - Playlist: https://www.youtube.com/playlist?list=...')
    print('  - Kanal Videos: https://www.youtube.com/@channelname/videos')
    print('  - Suche: https://www.youtube.com/results?search_query=...')
    
    url = input('\nYouTube URL eingeben: ').strip()
    
    if not url:
        print('❌ Keine URL eingegeben!')
        exit()
    
    try:
        num_videos = int(input('Wie viele Videos sammeln? (Standard: 10): ') or '10')
    except:
        num_videos = 10
    
    print('\n' + '=' * 60)
    links = extract_youtube_links(url, num_videos)
    
    if not links:
        print('\n❌ Keine Links gefunden!')
        exit()
    
    # Prüfe gegen dataset.csv, completed_downloads.csv UND videos/ Ordner
    existing_in_dataset = load_existing_links('dataset.csv')
    existing_in_completed = load_existing_links('completed_downloads.csv')
    downloaded_video_ids = get_downloaded_video_ids('videos')
    
    print(f'\nPrüfe vorhandene Videos...')
    print(f'  - In dataset.csv: {len(existing_in_dataset)}')
    print(f'  - In completed_downloads.csv: {len(existing_in_completed)}')
    print(f'  - Im videos/ Ordner: {len(downloaded_video_ids)}')
    
    # Filtere neue Links
    new_links = []
    for link in links:
        video_id = extract_video_id(link)
        
        # Prüfe ob Link oder Video-ID bereits existiert
        if link not in existing_in_dataset and \
           link not in existing_in_completed and \
           video_id not in downloaded_video_ids:
            new_links.append(link)
    
    print('\n' + '=' * 60)
    print(f'Gefundene Links: {len(links)}')
    print(f'Bereits vorhanden: {len(links) - len(new_links)}')
    print(f'Neue Links: {len(new_links)}')
    print('=' * 60)
    
    if new_links:
        print('\nNeue Links:')
        print('-' * 60)
        for i, link in enumerate(new_links, 1):
            video_id = extract_video_id(link)
            print(f'{i}. {link} [{video_id}]')
        
        save_to_file(new_links, 'dataset.csv', mode='a')
        print('\n✓ Fertig! Neue Links hinzugefügt.')
        print(f'\nDu kannst jetzt:')
        print(f'  1. downloader.py ausführen (lädt die {len(new_links)} neuen Videos)')
        print(f'  2. Pause machen')
        print(f'  3. extract_youtube_links.py erneut ausführen für die nächsten {num_videos} Videos')
    else:
        print('\n✓ Keine neuen Links zum Hinzufügen.')
        print('Alle gefundenen Videos sind bereits vorhanden oder heruntergeladen.')