from core.signal_collector import collect
from core.friction_detector import detect
from core.problem_normalizer import normalize
from core.problem_cluster import cluster
from core.problem_filter import filter_problems
from core.telemetry_loop import record_telemetry
from generator.tool_idea_generator import generate
from generator.feasibility_gate import evaluate_feasibility
from generator.webapp_builder import build_webapp

from radar.radar_collectors import collect_from_radar
from radar.signal_normalizer import normalize_signals
from radar.source_weighting import assign_weights
from radar.weak_signal_detector import detect_weak_signals
from radar.radar_output import output_to_pipeline

def main():
    metrics = {
        "signals_collected": 0,
        "problems_detected": 0,
        "problems_accepted": 0,
        "tool_name_generated": None,
        "build_success": False
    }

    try:
        print("--- DISCOVERY RADAR ---")
        radar_raw = collect_from_radar()
        radar_norm = normalize_signals(radar_raw)
        radar_weighted = assign_weights(radar_norm)
        emerging = detect_weak_signals(radar_weighted)
        radar_signals = output_to_pipeline(emerging)
        
        print("\n--- CORE PIPELINE ---")
        print("Collecting normal signals...")
        signals = collect()
        # Combine radar signals with normal signals
        signals.extend(radar_signals)
        metrics["signals_collected"] = len(signals)
        
        print("Detecting problems...")
        problems = detect(signals)
        metrics["problems_detected"] = len(problems)
        
        print("Normalizing problems...")
        normalized_problems = normalize(problems)
        
        print("Clustering problems...")
        clusters = cluster(normalized_problems)
        
        print("Filtering and ranking problems...")
        top_opportunities = filter_problems(clusters)
        metrics["problems_accepted"] = len(top_opportunities)
        
        built = False
        if top_opportunities:
            # Try to build the highest ranked feasible idea
            for best_problem in top_opportunities:
                print(f"Generating tool idea for problem: {best_problem.get('problem')}")
                
                # generate() should now take a single problem dict, so wrap in list for backward compat 
                # or pass the problem directly. We will pass a single-item list.
                idea = generate([best_problem])
                
                if idea:
                    if evaluate_feasibility(idea):
                        metrics["tool_name_generated"] = idea.get('tool_name')
                        build_webapp(idea)
                        built = True
                        metrics["build_success"] = True
                        break
                    else:
                        print(f"Skipping {idea.get('tool_name')} due to feasibility constraints. Trying next...")
        else:
            print("No valid opportunities found.")
            
    except Exception as e:
        print(f"Pipeline failed: {e}")
        
    finally:
        record_telemetry(metrics)

if __name__ == "__main__":
    main()
