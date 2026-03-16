def output_to_pipeline(emerging_problems):
    """
    Send validated emerging problems to the Problem OS pipeline as new signals.
    """
    print("Radar: Transferring emerging problems to core pipeline...")
    
    core_signals = []
    for ep in emerging_problems:
        core_signals.append({
            "id": f"radar_{hash(ep['problem']) % 10000}",
            "source": f"Discovery Radar ({', '.join(ep['sources'])})",
            "text": ep['problem'],
            "radar_confidence": ep['confidence']
        })
        
    print(f"Radar: Dispatched {len(core_signals)} signals downstream.")
    return core_signals
