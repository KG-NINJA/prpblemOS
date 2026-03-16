def assign_weights(signals):
    """
    Assigns a reliability weight to each signal based on its mapped source factor.
    Must remain under 150 lines.
    """
    print("Radar: Assigning source weights...")
    
    weight_map = {
        "github_issue": 1.0,
        "app_review": 0.9,
        "autocomplete": 0.8,
        "reddit": 0.7,
        "hackernews": 0.5
    }
    
    weighted_signals = []
    for sig in signals:
        source = sig.get("source", "unknown").lower()
        base_weight = weight_map.get(source, 0.5)  # default to lowest bound if unknown
        
        sig["weight"] = base_weight
        weighted_signals.append(sig)
        
    return weighted_signals
