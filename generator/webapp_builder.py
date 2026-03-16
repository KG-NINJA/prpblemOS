import json
import os
import urllib.request

def build_webapp(tool_idea):
    """
    Generate a minimal HTML+JS tool using templates/webapp.
    Output overwrites script.js to implement the tool.
    """
    print(f"Building webapp for: {tool_idea.get('tool_name')}...")
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Using mock script.js.")
        mock_js = "function run() {\n  const input = document.getElementById('input').value;\n  document.getElementById('output').innerText = 'Mock Processed: ' + input;\n}"
        with open('templates/webapp/script.js', 'w', encoding='utf-8') as f:
            f.write(mock_js)
        print("Done building mock webapp.")
        return

    prompt = f"""You are a senior javascript developer. Write ONLY the raw JavaScript code for this tool.
Do not output markdown code blocks. Only the raw js code.

Tool Name: {tool_idea.get('tool_name')}
Description: {tool_idea.get('description')}
Core Function: {tool_idea.get('core_function')}

The UI already has:
<textarea id="input"></textarea>
<button onclick="run()">Run</button>
<pre id="output"></pre>

Implement the `run()` function to read from `input`, process it based on the tool's core function, and write strictly to `output`.
Keep it under 200 lines. Use minimal or no external dependencies, relying on browser APIs where possible.
Always include error handling via try/catch and print errors to `output`.
"""

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a code generator. Output ONLY raw javascript. No markdown, no explanation."},
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            js_code = result['choices'][0]['message']['content']
            
            # Sanitize the output
            js_code = js_code.replace("```javascript", "").replace("```js", "").replace("```", "").strip()
            
            with open('templates/webapp/script.js', 'w', encoding='utf-8') as f:
                f.write(js_code)
            print("Successfully wrote templates/webapp/script.js. Project generated!")
    except Exception as e:
        print(f"Error generating tool code: {e}")
