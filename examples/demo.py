import os
import textwrap
import s2mflow

if __name__ == "__main__":
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in locals() else "."
    EXAMPLES_DIR = os.path.abspath(SCRIPT_DIR)
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

    NUM_COMMODITIES = 3
    SEED = 512

    exp_file = os.path.join(EXAMPLES_DIR, "exp_network.min")
    with open(exp_file, "w") as f:
        f.write(EXP_DATA)

    print(f"Created baseline file: {exp_file}")

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

    print("uniform supplies: ")
    print(uniform_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(uniform_mc_data.supply_partition, network.supplies))

    output_path = os.path.join(EXAMPLES_DIR, "uniform.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, uniform_mc_data)

    loaded_uniform_mc_data = s2mflow.load_multi_commodity_instance(output_path)

    print("-" * 20, "Spread Partitioning", "-" * 20)
    spread_mc_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=0,
        randomize_caps=False,
        randomize_costs=False,
        seed=SEED,
    )
    print("spread supplies: ")
    print(spread_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(spread_mc_data.supply_partition, network.supplies))
    
    output_path = os.path.join(EXAMPLES_DIR, "spread.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_data)

    loaded_spread_mc_data = s2mflow.load_multi_commodity_instance(output_path)

    print("-" * 20, "Beta-Binomial Partitioning", "-" * 20)
    beta_binomial_mc_data = s2mflow.generate_multi_commodity_data(
        instance=network,
        num_commodities=NUM_COMMODITIES,
        method=2,
        randomize_caps=False,
        randomize_costs=False,
        seed=SEED,
    )
    print("beta-binomial supplies: ")
    print(beta_binomial_mc_data.supply_partition)
    print("CDH: ", s2mflow.compute_commodity_demand_heterogeneity(beta_binomial_mc_data.supply_partition, network.supplies))

    output_path = os.path.join(EXAMPLES_DIR, "beta_binomial.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, beta_binomial_mc_data)

    loaded_beta_binomial_mc_data = s2mflow.load_multi_commodity_instance(output_path)

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

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_caps.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_caps_data)

    loaded_spread_mc_rand_caps_data = s2mflow.load_multi_commodity_instance(output_path)

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

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_costs.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_costs_data)

    loaded_spread_mc_rand_costs_data = s2mflow.load_multi_commodity_instance(output_path)

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

    output_path = os.path.join(EXAMPLES_DIR, "spread_rand_caps_costs.mcfmin")
    s2mflow.save_multi_commodity_instance(output_path, network, spread_mc_rand_caps_costs_data)

    loaded_spread_mc_rand_caps_costs_data = s2mflow.load_multi_commodity_instance(output_path)

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
        seed=SEED,
    )

    print(spread_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(spread_multi_data, data))
    print(uniform_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(uniform_multi_data, data))
    print(beta_binomial_multi_data)
    print(s2mflow.compute_commodity_demand_heterogeneity(beta_binomial_multi_data, data))

    incoming, outgoing = s2mflow.get_adjacency_mapping(network.nodes, network.arcs)
    print(incoming)
    print(outgoing)
