import time
from pathlib import Path
import s2mflow

def run_benchmark():
    # --- Configuration ---
    DATA_DIR = Path("data")
    INSTANCES = [
        "netgen_sr_08a/netgen_sr_08a.min",
        "netgen_sr_10a/netgen_sr_10a.min",
        "netgen_sr_11a/netgen_sr_11a.min",
        "netgen_sr_12a/netgen_sr_12a.min",
        "netgen_sr_13a/netgen_sr_13a.min",
        "netgen_sr_14a/netgen_sr_14a.min"
    ]
    COMMODITIES = [2, 5, 10, 20, 30, 50]
    OUTPUT_TXT = DATA_DIR / "benchmark_results.txt"
    SEED = 512
    CLEANUP_FILES = True  # Automatically delete temporary .mcfmin files

    # Define our two experimental cases
    CONFIGS = {
        "Std": {
            "is_uniform": False,
            "randomize_caps": False,
            "randomize_costs": False,
        },
        "Rand": {
            "is_uniform": False,
            "randomize_caps": True,
            "cap_a": 0.8,
            "cap_b": 1.0,
            "randomize_costs": True,
            "cost_a": 0.5,
            "cost_b": 2.0,
        }
    }

    # Expanded table formatting definitions to accommodate structural parameters
    headers = [
        "Instance", "Nodes", "Arcs", "K", "Srcs", "Dmds", 
        "Tot Demand", "Load Min(s)", "Generate(s)", "Write MCF(s)", "Load MCF(s)", "Total(s)"
    ]
    fmt_header = "{:<16} {:>8} {:>8} {:>3} {:>5} {:>5} {:>12} {:>12} {:>12} {:>12} {:>12} {:>10}"
    fmt_row    = "{:<16} {:>8,} {:>8,} {:>3} {:>5} {:>5} {:>12,.1f} {:>12.4f} {:>12.4f} {:>12.4f} {:>12.4f} {:>10.4f}"
    
    output_lines = []
    border = "-" * 126
    output_lines.append(border)
    output_lines.append(fmt_header.format(*headers))
    output_lines.append(border)

    print(f"{'='*70}")
    print("Starting s2mflow Comprehensive Performance & Metadata Benchmark")
    print(f"{'='*70}\n")

    for rel_path in INSTANCES:
        file_path = DATA_DIR / rel_path
        instance_name = file_path.stem
        
        if not file_path.exists():
            print(f"Warning: File not found -> {file_path}")
            continue
            
        print(f"Analyzing & benchmarking topology: {instance_name}...")
        
        # 1. Benchmark: Load base .min file
        t0 = time.perf_counter()
        network = s2mflow.load_min_instance(str(file_path))
        time_load_min = time.perf_counter() - t0

        for k in COMMODITIES:
            for variant_name, params in CONFIGS.items():
                # 2. Benchmark: Generate Multicommodity Data
                t0 = time.perf_counter()
                mc_data = s2mflow.generate_multi_commodity_data(
                    instance=network,
                    num_commodities=k,
                    seed=SEED,
                    **params,
                )
                time_gen = time.perf_counter() - t0
                
                # --- Extract Instance Structural Metadata Safely ---
                num_sources = 0
                num_demands = 0
                total_demand_val = 0.0
                
                if hasattr(mc_data, 'supply_partition') and isinstance(mc_data.supply_partition, dict):
                    for node, values in mc_data.supply_partition.items():
                        try:
                            # Identify if node acts as a source or demand across any commodity
                            has_src = any(v > 1e-5 for v in values)
                            has_dmd = any(v < -1e-5 for v in values)
                            # Accumulate total positive supply (equals total negative demand)
                            pos_sum = sum(v for v in values if v > 1e-5)
                            
                            if has_src:
                                num_sources += 1
                            if has_dmd:
                                num_demands += 1
                            total_demand_val += pos_sum
                        except TypeError:
                            # Fallback handling in case of flat scalar representations
                            if values > 1e-5:
                                num_sources += 1
                                total_demand_val += values
                            elif values < -1e-5:
                                num_demands += 1
                
                # 3. Benchmark: Write .mcfmin file
                out_mcfmin = file_path.with_suffix(f".k{k}.{variant_name.lower()}.mcfmin")
                t0 = time.perf_counter()
                s2mflow.save_multi_commodity_instance(str(out_mcfmin), network, mc_data)
                time_save = time.perf_counter() - t0
                
                # 4. Benchmark: Load .mcfmin file
                t0 = time.perf_counter()
                _ = s2mflow.load_multi_commodity_instance(str(out_mcfmin))
                time_load_mcfmin = time.perf_counter() - t0
                
                # Compute cumulative runtime duration
                total_pipeline = time_load_min + time_gen + time_save + time_load_mcfmin
                
                # Append complete row to output dataset
                row_str = fmt_row.format(
                    instance_name, network.num_nodes, network.num_arcs, k,
                    num_sources, num_demands, total_demand_val,
                    time_load_min, time_gen, time_save, time_load_mcfmin, total_pipeline
                )
                output_lines.append(row_str)
                
                # Cleanup temporary file
                if CLEANUP_FILES:
                    out_mcfmin.unlink(missing_ok=True)
                    
        output_lines.append(border)

    # Compile dataset into clear string structure
    final_table_string = "\n".join(output_lines)
    
    print("\nBENCHMARK METRICS & RESULTS:\n")
    print(final_table_string)
    
    # Save output to text file
    try:
        with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
            f.write(final_table_string + "\n")
        print(f"\nResults successfully saved to: {OUTPUT_TXT}")
    except IOError as e:
        print(f"\nFailed to write text file: {e}")

if __name__ == "__main__":
    run_benchmark()