import os
import glob
import pytest
import s2mflow


DATA_DIR = os.getenv("S2MFLOW_DATA_DIR", "data")

def discover_real_min_files():
    search_pattern = os.path.join(DATA_DIR, "**", "*.min")
    found_files = glob.glob(search_pattern, recursive=True)

    allowed_instances = {"netgen_1.min"}
    filtered_files = [
        f for f in found_files
        if os.path.basename(f) in allowed_instances
    ]

    return sorted([os.path.abspath(f) for f in filtered_files])


REAL_MIN_INSTANCES = discover_real_min_files()

@pytest.mark.skipif(not REAL_MIN_INSTANCES, reason="No .min instances found inside data.")
@pytest.mark.parametrize("input_min_file", REAL_MIN_INSTANCES)
@pytest.mark.parametrize("is_uniform", [True, False])
@pytest.mark.parametrize("num_commodities", [2, 3, 5, 10])
def test_partition_logic(input_min_file, is_uniform, num_commodities):
    """
    Verifies that the multicommody instance generation is correct:
    1. Sign Consistency
    2. Local Partitioning: sum_k(b_i^k) == b_i for each i.
    3. Global Balance: sum_i(b_i^k) == 0 for each k.
    """
    base_name = os.path.basename(input_min_file)

    # 1. Load the single-commodity instance
    network = s2mflow.load_min_instance(input_min_file)

    seed = 42

    mc_data = s2mflow.generate_multi_commodity_data(
        network,
        num_commodities=num_commodities,
        is_uniform=is_uniform,
        randomize_caps=False,
        cap_a=1.0,
        cap_b=1.0,
        randomize_costs=False,
        cost_a=1.0,
        cost_b=1.0,
        seed=seed,
    )

    for node_id, partitioned_vals in mc_data.supply_partition.items():
        original_supply = network.supplies.get(node_id, 0)

        # Local Balance
        local_sum = sum(partitioned_vals)
        assert local_sum == original_supply, \
            f"Local balance broken at node {node_id} in {base_name} (Uniform={is_uniform}, K={num_commodities})." \
            f"Got sum={local_sum}, expected={original_supply}"
        
        # Sign Consistency
        for val in partitioned_vals:
            if original_supply > 0:
                assert val >= 0, \
                    f"Sign violation in {base_name}: Supply node {node_id} with: {val} (Uniform={is_uniform}, K={num_commodities}, org={original_supply})."
            elif original_supply < 0:
                assert val <= 0, \
                    f"Sign violation in {base_name}: Demand node {node_id} with: {val} (Uniform={is_uniform}, K={num_commodities}, org={original_supply})."

    # Global Balance
    for k in range(num_commodities):
        commodity_global_sum = sum(node_vals[k] for node_vals in mc_data.supply_partition.values())
        assert commodity_global_sum == 0, \
            f"Global balance broken for commodity {k} in {base_name} (Uniform={is_uniform}, K={num_commodities})."


    