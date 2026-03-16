import json
import urllib.request
import os

def collect_from_radar():
    """
    Collects raw signals from Reddit, GitHub Issues, HackerNews posts, and Google Autocomplete.
    Returns a list of raw signal objects. Keep it under 150 lines.
    """
    print("Radar: Collecting from multiple sources...")
    os.makedirs('runtime', exist_ok=True)
    signals = []
    
    # 1. HackerNews (Ask HN) -> Weight 0.5
    try:
        url = "https://hacker-news.firebaseio.com/v0/askstories.json"
        req = urllib.request.Request(url, headers={'User-Agent': 'ProblemOS/1.0'})
        with urllib.request.urlopen(req) as res:
            ids = json.loads(res.read().decode('utf-8'))
            
        for sid in ids[:3]: # Keep payload small
            item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
            with urllib.request.urlopen(item_url) as res_item:
                item = json.loads(res_item.read().decode('utf-8'))
                if item and 'title' in item:
                    text_content = item.get('text', '')
                    title = item.get('title', '')
                    
                    signals.append({
                        "text": f"Title: {title}\nBody: {text_content}",
                        "source": "hackernews"
                    })
    except Exception as e:
        print(f"Radar: HN error {e}")
        
    # 2. Reddit (Programming / WebDev) -> Weight 0.7
    try:
        for sub in ['webdev', 'programming']:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=3"
            req = urllib.request.Request(url, headers={'User-Agent': 'ProblemOS/1.0'})
            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                for post in data['data']['children']:
                    pdata = post['data']
                    title = pdata.get('title', '')
                    selftext = pdata.get('selftext', '')
                    signals.append({
                        "text": f"Title: {title}\nBody: {selftext}",
                        "source": "reddit"
                    })
    except Exception as e:
        print(f"Radar: Reddit error {e}")
        
    # 3. GitHub Issues (Good first issues, etc.) -> Weight 1.0
    try:
        url = "https://api.github.com/search/issues?q=label:bug+state:open&per_page=3"
        req = urllib.request.Request(url, headers={'User-Agent': 'ProblemOS/1.0'})
        with urllib.request.urlopen(req) as res:
            data = json.loads(res.read().decode('utf-8'))
            for issue in data.get('items', []):
                title = issue.get('title', '')
                body = issue.get('body', '')
                signals.append({
                    "text": f"Issue: {title}\nBody: {body[:300]}",
                    "source": "github_issue"
                })
    except Exception as e:
        print(f"Radar: GitHub error {e}")
        
    # 4. Mock Autocomplete / App review -> Weight 0.8
    mock_autocompletes = [
        {"text": "how to change PDF metadata online free", "source": "autocomplete"},
        {"text": "why is making an app icon rounded so hard", "source": "autocomplete"},
    ]
    signals.extend(mock_autocompletes)
    
    with open('runtime/radar_signals.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
        
    print(f"Radar: Collected {len(signals)} raw multi-source signals.")
    return signals

if __name__ == "__main__":
    collect_from_radar()
