import json
import math
import os
import urllib.request

def get_embedding(text, api_key):
    url = "https://api.openai.com/v1/embeddings"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    data = {"input": text, "model": "text-embedding-3-small"}
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        res = json.loads(response.read().decode('utf-8'))
        return res['data'][0]['embedding']

def cosine_similarity(v1, v2):
    dot = sum(a*b for a, b in zip(v1, v2))
    m1 = math.sqrt(sum(a*a for a in v1))
    m2 = math.sqrt(sum(b*b for b in v2))
    return dot / (m1 * m2) if m1 and m2 else 0

def detect_weak_signals(weighted_signals):
    """
    Detects emerging problems appearing in multiple sources but with low frequency.
    """
    print("Radar: Identifying weak signals across sources...")
    os.makedirs('runtime', exist_ok=True)
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: Skipping embeddings (No API key).")
        return []
        
    for s in weighted_signals:
        try:
            s['embedding'] = get_embedding(s.get('text', ''), api_key)
        except Exception:
            s['embedding'] = [0] * 1536
            
    # Semantic grouping
    clusters = []
    used = set()
    for i, s1 in enumerate(weighted_signals):
        if i in used: continue
        current_cluster = [s1]
        used.add(i)
        for j, s2 in enumerate(weighted_signals):
            if j in used: continue
            if cosine_similarity(s1['embedding'], s2['embedding']) > 0.65:
                current_cluster.append(s2)
                used.add(j)
        clusters.append(current_cluster)
        
    emerging = []
    for c in clusters:
        sources = list(set([s.get('source') for s in c]))
        # Identify clusters spanning >= 2 sources
        if len(sources) >= 2:
            avg_weight = sum([s.get('weight', 0) for s in c]) / len(c)
            # Higher confidence if supported by multiple diverse sources with high weight
            confidence = min(1.0, round(avg_weight * 0.5 + (len(sources) * 0.1), 3))
            
            emerging.append({
                "problem": c[0].get('text', 'Unknown problem'),
                "cluster_size": len(c),
                "sources": sources,
                "confidence": confidence
            })
            
    with open('runtime/weak_signals.json', 'w', encoding='utf-8') as f:
        json.dump(emerging, f, indent=2, ensure_ascii=False)
        
    print(f"Radar: Found {len(emerging)} weak multi-source signals.")
    return emerging
