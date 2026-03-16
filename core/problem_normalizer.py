import json
import os
import urllib.request

def normalize(problems):
    """
    Normalizes the raw problems extracted by friction_detector.
    Uses an LLM to strip personal context, fix grammar, and output a standardized problem statement.
    """
    print(f"Normalizing {len(problems)} problems...")
    os.makedirs('runtime', exist_ok=True)
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Skipping normalization.")
        return problems

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    normalized_problems = []
    
    for p in problems:
        raw_prob = p.get('problem', '')
        if not raw_prob:
            normalized_problems.append(p)
            continue
            
        print(f"  Normalizing: {raw_prob[:50]}...")
        
        prompt = f"""You are a technical analyst. Re-write the following user frustration into a clean, objective problem statement.
Strip all personal context and rants. Focus only on the core friction.

Raw: {raw_prob}

Output purely JSON matching this structure exactly:
{{
  "normalized_problem": "string"
}}
"""
        
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
                norm_data = json.loads(content)
                
                # Update the problem string with the normalized version
                norm_str = norm_data.get('normalized_problem', raw_prob)
                p['problem'] = norm_str
                p['normalized'] = True
                
        except Exception as e:
            print(f"Error normalizing problem: {e}")
            
        normalized_problems.append(p)
            
    with open('runtime/normalized_problems.json', 'w', encoding='utf-8') as f:
        json.dump(normalized_problems, f, indent=2, ensure_ascii=False)
        
    print(f"Normalized {len(normalized_problems)} problems.")
    return normalized_problems
