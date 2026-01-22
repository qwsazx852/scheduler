import requests

ENDPOINTS = [
    ("Daily JSON", "https://trends.google.com/trends/api/dailytrends?hl=zh-TW&geo=TW&ns=15"),
    ("Realtime JSON", "https://trends.google.com/trends/api/realtimetrends?hl=zh-TW&geo=TW&cat=all"),
    ("Daily RSS", "https://trends.google.com/trends/trendingsearches/daily/rss?geo=TW"),
    ("Atom Feed", "https://trends.google.com/trends/hottrends/atom/feed?pn=p12"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://trends.google.com/trends/",
    "Cookie": "NID=511=test" # Minimal cookie
}

print("Testing connections from Python...")
print("-" * 50)

for name, url in ENDPOINTS:
    try:
        print(f"Testing {name}...")
        res = requests.get(url, headers=HEADERS, timeout=5)
        print(f"  -> Status: {res.status_code}")
        if res.status_code == 200:
            print(f"  -> SUCCESS! Content start: {res.text[:50]}")
        else:
            print(f"  -> Failed.")
    except Exception as e:
        print(f"  -> Exception: {e}")
    print("-" * 50)
