import os
import glob
import pytest
import s2mflow

DATA_DIR = os.getenv("S2MFLOW_DATA_DIR", "../s2mflow_data")

def get_min_instances():
    search_pattern = os.path.join(DATA_DIR, "**", "*.min")
    found_files = glob.glob(search_pattern, recursive=True)
    return sorted([os.path.abspath(f) for f in found_files])

INSTANCES = get_min_instances()

@pytest.mark.skipif(not INSTANCES, reason="No .min instances found inside s2mflow_data.")
@pytest.mark.parametrize("input_file", INSTANCES)
@pytest.mark.parametrize("is_uniform", [True, False])
@pytest.mark.parametrize("randomize_caps", [True, False])
@pytest.mark.parametrize("randomize_costs", [True, False])
@pytest.mark.parametrize("num_commodities", [2, 3, 5])
def test_round_trip(
    tmp_path, input_file, is_uniform, randomize_caps, randomize_costs, num_commodities
):
    """Verifies that saved and loaded file content matches the generated multicommodity data."""
    base_name = os.path.basename(input_file)
    output_path = tmp_path / f"rt_{base_name}_u{is_uniform}_k{num_commodities}_rcap{randomize_caps}_rcost{randomize_costs}.mcfmin"

    network = s2mflow.load_min_instance(input_file)
    seed = 42

    generated_mc_data = s2mflow.generate_multi_commodity_data(
        network,
        num_commodities=num_commodities,
        is_uniform=is_uniform,
        randomize_caps=randomize_caps,
        cap_a=0.8,
        cap_b=1.2,
        randomize_costs=randomize_costs,
        cost_a=0.8,
        cost_b=1.2,
        seed=seed,
    )

    s2mflow.save_multi_commodity_instance(str(output_path), network, generated_mc_data)

    loaded_mc_data = s2mflow.load_multi_commodity_instance(str(output_path))

    # Asserts
    assert loaded_mc_data.num_nodes == network.num_nodes
    assert loaded_mc_data.num_arcs == network.num_arcs
    assert loaded_mc_data.num_commodities == num_commodities
    assert loaded_mc_data.is_uniform == is_uniform
    assert loaded_mc_data.randomized_capacities == randomize_caps
    assert loaded_mc_data.randomized_weights == randomize_costs

    # Seed check: uniform (seed = 0)
    expected_seed = 0 if (is_uniform and not randomize_caps and not randomize_costs) else seed
    assert loaded_mc_data.seed == expected_seed

    for node_id, gen_vals in generated_mc_data.supply_partition.items():
        assert loaded_mc_data.commodity_supply_demand_data[node_id] == gen_vals
    
    for i, edge in enumerate(network.edges):
        arc_key = (edge.tail, edge.head)
        assert loaded_mc_data.commodity_capacities[arc_key] == generated_mc_data.capacites_by_arc[i]
        assert loaded_mc_data.commodity_weights[arc_key] == generated_mc_data.weights_by_arc[i]

