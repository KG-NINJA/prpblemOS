import json
import os
import urllib.request
import math

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
    mag1 = math.sqrt(sum(a*a for a in v1))
    mag2 = math.sqrt(sum(b*b for b in v2))
    if mag1 == 0 or mag2 == 0: return 0
    return dot / (mag1 * mag2)

def cluster(problems):
    """
    Groups similar problems using embeddings or semantic similarity.
    """
    print(f"Clustering {len(problems)} problems...")
    os.makedirs('runtime', exist_ok=True)
    
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Putting all in one mock cluster.")
        clusters = [{"cluster_id": 1, "theme": "Mock Cluster", "problems": problems}]
        with open('runtime/clusters.json', 'w', encoding='utf-8') as f:
            json.dump(clusters, f, indent=2, ensure_ascii=False)
        return clusters

    # Extract Embeddings
    for p in problems:
        try:
            p['embedding'] = get_embedding(p.get('problem', ''), api_key)
        except Exception as e:
            print(f"  Embedding error: {e}")
            p['embedding'] = [0] * 1536
            
    # Simple semantic grouping (O(N^2) greedy)
    clusters = []
    used = set()
    
    for i, p1 in enumerate(problems):
        if i in used: continue
        
        current_cluster = [p1]
        used.add(i)
        
        for j, p2 in enumerate(problems):
            if j in used: continue
            sim = cosine_similarity(p1['embedding'], p2['embedding'])
            if sim > 0.6:  # Similarity threshold
                current_cluster.append(p2)
                used.add(j)
                
        # Remove embeddings to keep JSON clean
        for p in current_cluster:
            p.pop('embedding', None)
            
        clusters.append({
            "cluster_id": len(clusters) + 1,
            "problems": current_cluster
        })
        
    with open('runtime/clusters.json', 'w', encoding='utf-8') as f:
        json.dump(clusters, f, indent=2, ensure_ascii=False)
        
    print(f"Formed {len(clusters)} clusters.")
    return clusters
