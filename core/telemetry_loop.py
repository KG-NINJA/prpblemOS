import json
import os
import datetime

def record_telemetry(metrics):
    """
    Appends execution metrics to runtime/telemetry.json
    metrics should be a dict containing:
    - signals_collected
    - problems_detected
    - problems_accepted
    - tool_name_generated (or None)
    - build_success (bool)
    """
    os.makedirs('runtime', exist_ok=True)
    telemetry_file = 'runtime/telemetry.json'
    
    history = []
    if os.path.exists(telemetry_file):
        try:
            with open(telemetry_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except Exception:
            pass
            
    record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "metrics": metrics
    }
    history.append(record)
    
    # Calculate rolling targets for logs
    runs = len(history)
    tools_built = sum(1 for r in history if r['metrics'].get('build_success'))
    total_detected = sum(r['metrics'].get('problems_detected', 0) for r in history)
    total_accepted = sum(r['metrics'].get('problems_accepted', 0) for r in history)
    
    usable_ratio = round((tools_built / runs) * 100, 1) if runs > 0 else 0
    accuracy = round((total_accepted / total_detected) * 100, 1) if total_detected > 0 else 0
    
    print("\n--- Pipeline Telemetry ---")
    print(f"Target Metrics -> Usable tools ratio: {usable_ratio}% | Problem discovery accuracy (Filter Pass Rate): {accuracy}% | Tools Built Lifetime: {tools_built}")
    print("--------------------------\n")

    with open(telemetry_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)
