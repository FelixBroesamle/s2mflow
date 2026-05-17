import s2mflow
import pytest
import os
import glob
import time

def test_round_trip_dummy(tmp_path):
    """
    Verifies the full pipelinie:
    Load (.min) -> Generate (MCF) -> Save (.mcfmin) -> Load (.mcfmin)
    """

    # 1. Create a temporary dummy .min file
    input_path = tmp_path / "test_input.min"
    output_path = tmp_path / "test_output.mcfmin"

    with open(input_path, "w") as f:
        f.write("p min 2 1\n")
        f.write("n 1 10\n")
        f.write("n 2 -10\n")
        f.write("a 1 2 0 100 5\n")

    # 2. Load the single-commodity instance
    network = s2mflow.load_min_instance(str(input_path))
    assert network.num_nodes == 2
    assert network.supplies[1] == 10

    # 3. Lift to 3 commodities (using Spread)
    num_commodities = 3
    seed = 42
    mc_data = s2mflow.generate_multi_commodity_data(
        network,
        num_commodities=num_commodities,
        is_uniform=False,
        seed=seed
    )

    # 4. Save the result in the .mcfmin formal
    s2mflow.save_multi_commodity_instance(str(output_path), network, mc_data)

    # 5. Load the generated file back into Python
    loaded_mc_data = s2mflow.load_multi_commodity_instance(str(output_path))

    # ----- VERIFICATION ------

    # Metadata Check:
    assert loaded_mc_data.num_nodes == 2
    assert loaded_mc_data.num_arcs == 1
    assert loaded_mc_data.num_commodities == num_commodities
    assert loaded_mc_data.seed == seed
    assert loaded_mc_data.is_uniform is False

    # Lifting Check:
    # 1. Local Balance Check (Node-wise)
    for node_id, partitioned_vals in loaded_mc_data.commodity_supply_demand_data.items():
        original_supply = network.supplies[node_id]
        local_sum = sum(partitioned_vals)
        assert local_sum == original_supply, f"Local balance failed at node {node_id}: sum is {local_sum} (expected {original_supply})."
    
    # 2. Sign Consistency Check (Node-wise)
    for node_id, partitioned_vals in loaded_mc_data.commodity_supply_demand_data.items():
        original_supply = network.supplies[node_id]
        for val in partitioned_vals:
            if original_supply > 0:
                assert val >= 0, f"Sign error: Supply node {node_id} has negative commodity value {val}."
            elif original_supply < 0:
                assert val <= 0, f"Sign error: Demand node {node_id} has positive commodity value {val}."
    
    # 3. Global Balance Check (Commodity-wise)
    for k in range(num_commodities):
        k_sum = sum(
            node_vals[k] for node_vals in loaded_mc_data.commodity_supply_demand_data.values()
        )
        assert k_sum == 0