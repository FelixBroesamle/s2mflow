import os
import glob
import s2mflow

DATA_DIR = "data"
KS       = [2, 5, 10]
SEED     = 512

# Match the config used by examples/solve_instance_*.py, so the parsed-file
# workflow loads exactly what the generation workflow produces.
METHOD          = 0        # 0 = Spread
RANDOMIZE_CAPS  = False
RANDOMIZE_COSTS = False


def main() -> None:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, DATA_DIR)

    min_files = sorted(glob.glob(
        os.path.join(data_dir, "net_instance_*", "netgen_*.min")
    ))
    if not min_files:
        print(f"No .min files found under {data_dir}/net_instance_*/")
        return

    for min_file in min_files:
        folder = os.path.dirname(min_file)
        stem   = os.path.splitext(os.path.basename(min_file))[0]   # e.g. "netgen_1"
        network = s2mflow.load_min_instance(min_file)
        print(f"\n{min_file}")
        print(f"  nodes = {network.num_nodes}, arcs = {network.num_arcs}, "
              f"parallel = {network.parallel}")

        for k in KS:
            md = s2mflow.generate_multi_commodity_data(
                instance=network,
                num_commodities=k,
                method=METHOD,
                randomize_caps=RANDOMIZE_CAPS,
                randomize_costs=RANDOMIZE_COSTS,
                seed=SEED,
            )
            out = os.path.join(folder, f"{stem}_{k}.mcfmin")
            s2mflow.save_multi_commodity_instance(out, network, md)
            print(f"  -> {os.path.basename(out):<24} "
                  f"K={k:<3} arcs={len(md.commodity_edges)}")

    print("\nDone.")


if __name__ == "__main__":
    main()