import requests
import re
import json

# Test Desktop URL (Mobile yielded no JSON last time)
url = "https://www.youtube.com/feed/trending?gl=TW&hl=zh-TW"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-TW,zh;q=0.9",
}

try:
    print(f"Fetching {url}...")
    res = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Final URL: {res.url}")
    
    match = re.search(r'var ytInitialData = ({.*?});', res.text)
    if not match:
        # Fallback: try finding extracted JSON in other vars or just basic HTML parsing
        print("No ytInitialData found")
        exit(1)
        
    data = json.loads(match.group(1))
    
    # Drill down to tabs
    if 'contents' in data and 'twoColumnBrowseResultsRenderer' in data['contents']:
        tabs = data['contents']['twoColumnBrowseResultsRenderer']['tabs']
        print(f"Tabs count: {len(tabs)}")
        
        # Check first tab content
        content = tabs[0]['tabRenderer']['content']
        
        if 'richGridRenderer' in content:
            print("Found richGridRenderer! Scanning contents...")
            contents = content['richGridRenderer']['contents']
            print(f"Total items in grid: {len(contents)}")
            
            for idx, item in enumerate(contents):
                if 'richItemRenderer' in item:
                    # Normal Video
                    print(f"[{idx}] Found Video!")
                    vid = item['richItemRenderer']['content']['videoRenderer']
                    print("   Title:", vid.get('title', {}).get('runs', [{}])[0].get('text'))
                    
                elif 'richSectionRenderer' in item:
                    # Section (Nudge or Shelf)
                    print(f"[{idx}] Found Section")
                    sc = item['richSectionRenderer']['content']
                    if 'feedNudgeRenderer' in sc:
                         print("   !!! FOUND NUDGE !!!")
                         nudge = sc['feedNudgeRenderer']
                         title = nudge.get('title', {}).get('runs', [{}])[0].get('text', 'No Title')
                         # subtitle can be simpleText or runs
                         subtitle = "No Subtitle"
                         if 'subtitle' in nudge:
                             if 'runs' in nudge['subtitle']:
                                 subtitle = nudge['subtitle']['runs'][0]['text']
                             elif 'simpleText' in nudge['subtitle']:
                                 subtitle = nudge['subtitle']['simpleText']
                                 
                         print(f"   Nudge Message: {title}")
                         print(f"   Reason: {subtitle}")
                    elif 'richShelfRenderer' in sc:
                        print("   Found Shelf (Videos inside!)")
                        shelf_contents = sc['richShelfRenderer']['contents']
                        print(f"   Shelf Request: {len(shelf_contents)} items")
                        if len(shelf_contents) > 0:
                            v = shelf_contents[0]['richItemRenderer']['content']['videoRenderer']
                            print("   Ex Title:", v.get('title', {}).get('runs', [{}])[0].get('text'))
    else:
        print("Unexpected top-level structure:", data.keys())

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
