import json
import os

def rank(clusters):
    """
    Scores problems by frequency, difficulty, monetization potential.
    """
    print(f"Ranking {len(clusters)} opportunity clusters...")
    os.makedirs('runtime', exist_ok=True)
    
    scored_opportunities = []
    
    for c in clusters:
        frequency = len(c['problems'])
        diff_score = 0
        urgency_score = 0
        
        for p in c['problems']:
            diff = p.get('difficulty', '').lower()
            urg = p.get('urgency', '').lower()
            
            if diff == 'high': diff_score += 3
            elif diff == 'medium': diff_score += 2
            else: diff_score += 1
            
            if urg == 'high': urgency_score += 3
            elif urg == 'medium': urgency_score += 2
            else: urgency_score += 1
            
        # Monetization potential heuristic
        monetization_potential = urgency_score * 1.5 
        
        total_score = (frequency * 5) + diff_score + monetization_potential
        
        best_problem = c['problems'][0].get('problem', 'Unknown') if c['problems'] else "Unknown"
        
        scored_opportunities.append({
            "cluster_id": c['cluster_id'],
            "representative_problem": best_problem,
            "score": total_score,
            "metrics": {
                "frequency": frequency,
                "difficulty_score": diff_score,
                "urgency_score": urgency_score,
                "monetization": monetization_potential
            }
        })
        
    # Sort descending
    scored_opportunities.sort(key=lambda x: x['score'], reverse=True)
    
    with open('runtime/opportunities.json', 'w', encoding='utf-8') as f:
        json.dump(scored_opportunities, f, indent=2, ensure_ascii=False)
        
    top_problems = scored_opportunities[:3]
    top_prob_text = top_problems[0]['representative_problem'] if top_problems else "None"
    print(f"Top ranked problem: {top_prob_text}")
    
    return top_problems
