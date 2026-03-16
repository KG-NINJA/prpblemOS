import json
import os
import urllib.request
from .webapp_builder import build_webapp

def generate(top_problems):
    """
    Converts highest ranked problems into minimal web tool ideas.
    Then triggers the webapp builder for the top idea.
    """
    print(f"Generating tool ideas for top {len(top_problems)} problems...")
    os.makedirs('runtime', exist_ok=True)
    
    with open('prompts/tool_prompt.md', 'r', encoding='utf-8') as f:
        prompt_template = f.read()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Using mock tool idea.")
        mock_idea = {
            "tool_name": "Mock Tool IDE",
            "description": "A browser tool built automatically",
            "core_function": "Reads input and outputs it"
        }
        with open('runtime/tool_idea.json', 'w', encoding='utf-8') as f:
            json.dump(mock_idea, f, indent=2, ensure_ascii=False)
        print("Triggering webapp_builder with mock idea...")
        build_webapp(mock_idea)
        return mock_idea
        
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    if not top_problems:
        print("No problems to generate tools for.")
        return None
        
    # Pick the top ranked problem to build
    best_problem = top_problems[0]
    prompt = prompt_template.replace("{PROBLEM}", best_problem.get('problem', ''))
    
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You output JSON strictly."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    idea = None
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            content = result['choices'][0]['message']['content']
            idea = json.loads(content)
    except Exception as e:
        print(f"Error generating tool idea: {e}")
        return None

    if idea:
        with open('runtime/tool_idea.json', 'w', encoding='utf-8') as f:
            json.dump(idea, f, indent=2, ensure_ascii=False)
            
        print(f"Generated Tool Idea: {idea.get('tool_name')}")
        print("Triggering webapp_builder...")
        build_webapp(idea)
        
    return idea
