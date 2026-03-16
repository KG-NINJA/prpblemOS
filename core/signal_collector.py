import json
import urllib.request
import os

def collect():
    """
    Collects Ask HN posts to find user problems and frustrations.
    """
    os.makedirs('runtime', exist_ok=True)
    
    print("Fetching Ask HN stories for signals...")
    url = "https://hacker-news.firebaseio.com/v0/askstories.json"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'ProblemOS/1.0'})
        with urllib.request.urlopen(req) as response:
            story_ids = json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch Ask HN: {e}")
        return []

    signals = []
    # Grab the top 15 Ask HN posts
    for sid in story_ids[:15]:
        item_url = f"https://hacker-news.firebaseio.com/v0/item/{sid}.json"
        try:
            with urllib.request.urlopen(item_url) as res:
                item = json.loads(res.read().decode('utf-8'))
                if item and 'title' in item:
                    text_content = item.get('text', '')
                    title = item.get('title', '')
                    
                    # Ensure we have enough text to analyze
                    full_text = f"Title: {title}\nBody: {text_content}"
                    signals.append({
                        "id": sid,
                        "source": "HackerNews Ask",
                        "text": full_text
                    })
        except Exception as e:
            print(f"Error fetching item {sid}: {e}")
            
    # Save to runtime
    with open('runtime/signals.json', 'w', encoding='utf-8') as f:
        json.dump(signals, f, indent=2, ensure_ascii=False)
        
    print(f"Collected {len(signals)} signals and saved to runtime/signals.json.")
    return signals

if __name__ == "__main__":
    collect()
