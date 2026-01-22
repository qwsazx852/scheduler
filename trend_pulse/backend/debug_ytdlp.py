import yt_dlp
import json

def test_ytdlp_trending():
    print("Testing yt-dlp fetch for Trending...")
    
    # 'extract_flat': True is crucial for playlists/feeds to be fast (doesn't download video info details, just list)
    ydl_opts = {
        'extract_flat': True, 
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # YouTube Trending URL
            # Using mobile URL might be safer or desktop, let's try desktop first as yt-dlp handles it well usually
            url = "https://www.youtube.com/feed/trending?gl=TW&hl=zh-TW"
            info = ydl.extract_info(url, download=False)
            
            print(f"Title: {info.get('title')}")
            
            if 'entries' in info:
                entries = list(info['entries'])
                print(f"Found {len(entries)} entries.")
                
                for i, entry in enumerate(entries[:3]):
                    print(f"\n--- Entry {i+1} ---")
                    print(f"Title: {entry.get('title')}")
                    print(f"Channel: {entry.get('uploader')}")
                    print(f"Views: {entry.get('view_count')}")
                    print(f"ID: {entry.get('id')}")
            else:
                print("No entries found.")
                
    except Exception as e:
        print(f"yt-dlp Failed: {e}")

if __name__ == "__main__":
    test_ytdlp_trending()
