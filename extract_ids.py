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
    return None

# Lies deine Links-Datei
input_file = 'youtube_links.txt'  # Deine Datei mit den Links
output_file = 'dataset.csv'

with open(input_file, 'r', encoding='utf-8') as f:
    links = f.read().splitlines()

video_ids = []
for link in links:
    video_id = extract_video_id(link)
    if video_id:
        video_ids.append(video_id)
        print(f'Gefunden: {video_id} von {link}')
    else:
        print(f'Keine ID gefunden in: {link}')

# Schreibe IDs in dataset.csv
with open(output_file, 'w', encoding='utf-8') as f:
    for video_id in video_ids:
        f.write(video_id + '\n')

print(f'\n{len(video_ids)} Video-IDs in {output_file} gespeichert')
```

**Verwendung:**

1. Erstelle eine Datei `youtube_links.txt` mit deinen Links (eine URL pro Zeile):
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://youtu.be/jNQXAC9IVRw
https://www.youtube.com/watch?v=9bZkp7q19f0