import json
import urllib.request
import os

def normalize_signals(signals):
    """
    Clean text signals by removing usernames, URLs, and emotional language.
    Output normalized text signals. Must remain under 150 lines.
    """
    print("Radar: Normalizing incoming signals...")
    os.makedirs('runtime', exist_ok=True)
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Skipping text normalization.")
        return signals

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    clean_signals = []
    
    for sig in signals:
        raw_text = sig.get('text', '')
        if not raw_text or len(raw_text) < 10:
            clean_signals.append(sig)
            continue
            
        prompt = f"""Clean the following block of text representing a user issue/problem.
Remove all usernames, exact URLs, non-essential code blocks, and emotional language/rants.
Keep the core technical issue or frustration.

Raw Text:
{raw_text[:1000]}

Output JSON:
{{
  "normalized_text": "string"
}}
"""
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are an objective summarizer. Output strictly JSON."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                content = result['choices'][0]['message']['content']
                norm_data = json.loads(content)
                
                sig['text'] = norm_data.get('normalized_text', raw_text)
                
        except Exception as e:
            print(f"  Radar Normalization API error: {e}")
            
        clean_signals.append(sig)
        
    return clean_signals
