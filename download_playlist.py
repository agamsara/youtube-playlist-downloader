#!/usr/bin/env python3
"""
download_playlist.py: Download all songs from a playlist URL into a directory,
skipping any tracks that already exist in the target folder, and limit to the first 50 tracks.
Requirements:
  - Python 3.6+
  - yt-dlp (`pacman -S yt-dlp` or `python -m pip install yt-dlp`)
  - ffmpeg (for audio extraction)
Usage:
  python download_playlist.py <playlist_url> [output_dir]
"""
import os
import sys
import yt_dlp
def sanitize_filename(s: str) -> str:
    # Replace filesystem‑unfriendly characters
    return s.replace('/', '_').replace('\\', '_')
def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <playlist_url> [output_dir]")
        sys.exit(1)
    playlist_url = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) >= 3 else os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    # Step 1: List entries in the playlist without downloading
    list_opts = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }
    with yt_dlp.YoutubeDL(list_opts) as ydl:
        info = ydl.extract_info(playlist_url, download=False)
        entries = info.get('entries', [])
        print(f"Found {len(entries)} items in playlist.")
    # Limit to the first 50 entries
    entries = entries[:50]
    print(f"Processing first {len(entries)} items (limited to 50).")
    # Step 2: Prepare download options for audio extraction
    download_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
    }
    # Step 3: Iterate and download missing tracks
    for entry in entries:
        title = entry.get('title') or entry.get('id')
        sanitized = sanitize_filename(title)
        filename = os.path.join(output_dir, f"{sanitized}.mp3")
        if os.path.exists(filename):
            print(f"Skipping '{title}'; already exists.")
            continue
        # Construct full URL if necessary
        video_id = entry.get('id') or entry.get('url')
        if not video_id.startswith('http'):
            video_url = f"https://www.youtube.com/watch?v={video_id}"
        else:
            video_url = video_id
        print(f"Downloading '{title}'...")
        with yt_dlp.YoutubeDL(download_opts) as ydl2:
            ydl2.download([video_url])
if __name__ == '__main__':
    main()
