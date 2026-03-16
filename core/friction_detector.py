import json
import os
import urllib.request

def detect(signals):
    """
    Uses an LLM to extract user frustrations from signals and convert them into structured problems.
    """
    print(f"Detecting problems from {len(signals)} signals...")
    os.makedirs('runtime', exist_ok=True)
    
    with open('prompts/friction_prompt.md', 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Using mock problem data.")
        mock_problems = []
        for s in signals[:2]:
            mock_problems.append({
                "problem": f"Sample problem extracted from {s['id']}",
                "urgency": "medium",
                "difficulty": "medium",
                "source_id": s['id']
            })
        with open('runtime/frictions.json', 'w', encoding='utf-8') as f:
            json.dump(mock_problems, f, indent=2, ensure_ascii=False)
        return mock_problems

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    problems = []
    
    # Process up to 3 signals to keep latency low for prototype
    for count, signal in enumerate(signals[:3]):
        print(f"  Analyzing signal {signal['id']}...")
        prompt = prompt_template.replace("{TEXT}", signal['text'])
        
        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You output JSON strictly."},
                {"role": "user", "content": prompt}
            ],
            "response_format": {"type": "json_object"}
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                content = result['choices'][0]['message']['content']
                problem_data = json.loads(content)
                problem_data['source_id'] = signal['id']
                problems.append(problem_data)
        except Exception as e:
            print(f"  Error analyzing signal {signal['id']}: {e}")
            
    with open('runtime/frictions.json', 'w', encoding='utf-8') as f:
        json.dump(problems, f, indent=2, ensure_ascii=False)
        
    print(f"Detected {len(problems)} problems.")
    return problems

if __name__ == "__main__":
    with open('runtime/signals.json', 'r', encoding='utf-8') as f:
        sigs = json.load(f)
    detect(sigs)
