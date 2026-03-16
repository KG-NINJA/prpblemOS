import json
import os
import urllib.request

def evaluate_feasibility(tool_idea):
    """
    Evaluates a proposed tool idea and gates it if it requires a backend API, database, 
    or is too complex to fit in <300 lines of vanilla JavaScript.
    """
    print(f"Evaluating feasibility for: {tool_idea.get('tool_name')}...")
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Defaulting to passed.")
        return True

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"""Analyze the following web tool idea.
Tool Name: {tool_idea.get('tool_name')}
Description: {tool_idea.get('description')}
Core Function: {tool_idea.get('core_function')}

Can this application realistically be built entirely in < 300 lines of frontend-only, vanilla JavaScript and run entirely in a browser WITHOUT needing a backend REST API, database, or external auth?

Output purely JSON:
{{
  "feasible": boolean,
  "reason": "string"
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
            eval_data = json.loads(content)
            
            is_feasible = eval_data.get('feasible', False)
            reason = eval_data.get('reason', '')
            
            if is_feasible:
                print(f"Idea Feasible. Proceeding to generator. ({reason})")
            else:
                print(f"Idea NOT Feasible. Gated. ({reason})")
                
            return is_feasible
            
    except Exception as e:
        print(f"Error evaluating feasibility: {e}")
        return False
