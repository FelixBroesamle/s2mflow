import os
import textwrap
import s2mflow

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
    EXAMPLES_DIR = os.path.abspath(SCRIPT_DIR)
    PROJECT_ROOT = os.path.dirname(EXAMPLES_DIR)
    os.makedirs(EXAMPLES_DIR, exist_ok=True)

    # Single-Commodity Network (DIMACS .min)
    EXP_DATA = textwrap.dedent("""\
        p min 4 5
        n 1 17
        n 4 -17
        a 1 2 0 10 10
        a 1 3 0 15 5
        a 2 4 0 10 10
        a 3 2 0 5 20
        a 3 4 0 15 4
    """)

    NUM_COMMODITIES = 5
    SEED = 512

    exp_file = os.path.join(EXAMPLES_DIR, "exp_network.min")
    with open(exp_file, "w") as f:
        f.write(EXP_DATA)

    print(f"Created baseline file: {exp_file}")

    exp_file = os.path.join(EXAMPLES_DIR, "exp_network.min")
    network = s2mflow.load_min_instance(exp_file)
    print("network supplies: ")
    print(network.supplies)

    print("-" * 20, "Uniform Partitioning", "-" * 20)
    uniform_mc_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=1,
        randomize_caps=False,
        randomize_costs=False,
    )

    print(uniform_mc_data.seed)

    print("uniform supplies: ")
    print(uniform_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(uniform_mc_data.supply_partition, network.supplies))

    output_path = os.path.join(EXAMPLES_DIR, f"uniform.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, uniform_mc_data)

    loaded_uniform_mc_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_uniform_mc_data.seed)

    print("-" * 20, "Spread Partitioning", "-" * 20)
    spread_mc_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=False,
        randomize_costs=False,
        seed=SEED,
    )

    print(spread_mc_data.seed)

    print("spread supplies: ")
    print(spread_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(spread_mc_data.supply_partition, network.supplies))
    
    output_path = os.path.join(EXAMPLES_DIR, f"spread.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_data)

    loaded_spread_mc_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_mc_data.seed)

    print("-" * 20, "Beta-Binomial Partitioning", "-" * 20)
    beta_binomial_mc_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=2,
        randomize_caps=False,
        randomize_costs=False,
        concentration_param=30.0,
        seed=SEED,
    )

    print(beta_binomial_mc_data.seed)

    print("beta-binomial supplies: ")
    print(beta_binomial_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(beta_binomial_mc_data.supply_partition, network.supplies))

    output_path = os.path.join(EXAMPLES_DIR, f"beta_binomial.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, beta_binomial_mc_data)

    loaded_beta_binomial_mc_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_beta_binomial_mc_data.seed)

    print("-" * 20, "Spread Partitioning with randomized capacities", "-" * 20)
    spread_mc_rand_caps_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=True,
        cap_a=0.6,
        cap_b=1.0,
        randomize_costs=False,
        seed=SEED,
    )

    print(spread_mc_rand_caps_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_caps.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_caps_data)

    loaded_spread_mc_rand_caps_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_mc_rand_caps_data.seed)

    print("-" * 20, "Spread Partitioning with zero-capacity exclusions", "-" * 20)
    spread_zero_cap_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=False,
        randomize_costs=False,
        cap_zero=True,
        cap_zero_param=0.02,
        seed=SEED,
    )

    print(spread_zero_cap_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, f"spread_zero_cap.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_zero_cap_data)

    loaded_spread_zero_cap_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_zero_cap_data.seed)

    print("-" * 20, "Spread Partitioning with zero-capacity exclusions and randomized capacities", "-" * 20)
    spread_zero_cap_and_rand_caps_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=True,
        cap_a=0.8,
        cap_b=1.0,
        randomize_costs=False,
        cap_zero=True,
        cap_zero_param=0.02,
        seed=SEED,
    )

    print(spread_zero_cap_and_rand_caps_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, f"spread_zero_cap_rand_caps.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_zero_cap_and_rand_caps_data)

    loaded_spread_zero_cap_and_rand_caps_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_zero_cap_and_rand_caps_data.seed)

    print("-" * 20, "Spread Partitioning with zero-capacity exclusions, randomized capacities, and randomized costs", "-" * 20)
    spread_zero_cap_rand_caps_rand_costs_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=True,
        cap_a=0.6,
        cap_b=1.0,
        randomize_costs=True,
        cost_a=0.5,
        cost_b=2.0,
        cap_zero=True,
        cap_zero_param=0.05,
        seed=SEED,
    )

    print(spread_zero_cap_rand_caps_rand_costs_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, f"spread_zero_cap_rand_caps_rand_costs.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_zero_cap_rand_caps_rand_costs_data)

    loaded_spread_zero_cap_rand_caps_rand_costs_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_zero_cap_rand_caps_rand_costs_data.seed)

    print("-" * 20, "Spread Partitioning with randomized costs", "-" * 20)
    spread_mc_rand_costs_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=False,
        randomize_costs=True,
        cost_a=0.5,
        cost_b=2.0,
        seed=SEED,
    )

    print(spread_mc_rand_costs_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_costs.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_costs_data)

    loaded_spread_mc_rand_costs_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_mc_rand_costs_data.seed)

    print("-" * 20, "Spread Partitioning with randomized capacities and costs", "-" * 20)
    spread_mc_rand_caps_costs_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=True,
        cap_a=0.6,
        cap_b=1.0,
        randomize_costs=True,
        cost_a=0.5,
        cost_b=2.0,
        seed=SEED,
    )

    print(spread_mc_rand_caps_costs_data.seed)

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_caps_costs.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_caps_costs_data)

    loaded_spread_mc_rand_caps_costs_data = s2mflow.load_multi_commodity_instance(output_path)

    print(loaded_spread_mc_rand_caps_costs_data.seed)

    data = {1: 387, 2: -387}
    print(data)

    spread_multi_data = s2mflow.split_supplies_spread(
        data, 
        num_commodities=5, 
        seed=SEED
    )

    uniform_multi_data = s2mflow.split_supplies_uniform(
        data,
        num_commodities=5,
    )

    beta_binomial_multi_data = s2mflow.split_supplies_beta_binomial(
        data,
        num_commodities=5,
        concentration_param=5.0,
        seed=SEED,
    )

    print(spread_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(spread_multi_data, data))
    print(uniform_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(uniform_multi_data, data))
    print(beta_binomial_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(beta_binomial_multi_data, data))

    incoming, outgoing = s2mflow.get_adjacency_mapping(network.nodes, network.topology())
    #print(incoming)
    #print(outgoing)

    print("=" * 20, "Parallel-arc extension (0.3.0)", "=" * 20)

    # 1) Synthetic parallel instance: two arcs share the pair (1, 2) 
    PARALLEL_DATA = textwrap.dedent("""\
        c min 3 4
        n 1 10
        n 3 -10
        a 1 2 0 6 3
        a 1 2 0 4 2
        a 2 3 0 10 1
        a 1 3 0 10 5
    """)
    parallel_file = os.path.join(EXAMPLES_DIR, "exp_parallel.min")
    with open(parallel_file, "w") as f:
        f.write(PARALLEL_DATA)

    pnet = s2mflow.load_min_instance(parallel_file)

    print(f"  parallel            = {pnet.parallel}")
    print(f"  num_parallel_pairs  = {pnet.num_parallel_arc_pairs}")
    print(f"  arcs (tail, head, idx) = {pnet.arcs}")
    print(f"  arc_indices         = {pnet.arc_indices}")

    pmd = s2mflow.generate_multi_commodity_data(
        pnet, num_commodities=NUM_COMMODITIES, method=0, seed=SEED,
    )
    unique = len(pmd.commodity_capacities) == len(pnet.edges) == len(pnet.edges)
    print(f"  |edges| = {len(pnet.edges)}   |commodity_capacities| = {len(pmd.commodity_capacities)}"
          f"   unique keys = {unique}")

    pout = os.path.join(EXAMPLES_DIR, "exp_parallel.mcfmin")
    s2mflow.save_multi_commodity_instance(pout, pnet, pmd)
    pld = s2mflow.load_multi_commodity_instance(pout)
    print(f"  round-trip parallel = {pld.parallel}, "
          f"keys preserved = {len(pld.commodity_capacities) == len(pnet.edges)}")

     # -- 2) Real gridgen instance: run only if the data file is present ----------
    gridgen = os.path.join(PROJECT_ROOT, "data", "gridgen_1", "smcg_gridgen_1.min")
    if os.path.exists(gridgen):
        print("\n  -- Real gridgen instance --")
        gnet = s2mflow.load_min_instance(gridgen)
        print(f"  nodes / arcs        = {gnet.num_nodes} / {gnet.num_arcs}")
        print(f"  parallel            = {gnet.parallel}")
        print(f"  parallel pairs      = {gnet.num_parallel_arc_pairs}")

        gmd = s2mflow.generate_multi_commodity_data(
            gnet, num_commodities=NUM_COMMODITIES, method=0, seed=SEED,
        )
        unique = len(gmd.commodity_capacities) == len(gnet.edges)
        print(f"  |edges|             = {len(gnet.edges)}")
        print(f"  |commodity_caps|    = {len(gmd.commodity_capacities)}   unique keys = {unique}")

        
        gout = os.path.join(EXAMPLES_DIR, "gridgen_1.mcfmin")
        s2mflow.save_multi_commodity_instance(gout, gnet, gmd)
        gld = s2mflow.load_multi_commodity_instance(gout)
        print(f"  round-trip parallel = {gld.parallel}, "
              f"keys preserved = {len(gld.commodity_capacities) == len(gnet.edges)}")
    else:
        print(f"\n  [gridgen demo skipped — {gridgen} not found]")

    print("=" * 60)
    print("Demo complete.")
    print("=" * 60)
    
