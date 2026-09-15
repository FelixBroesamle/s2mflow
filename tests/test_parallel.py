"""Parallel-arc test: the (tail, head, index) key must never lose an arc."""
import os
import pytest
import s2mflow

DATA_DIR = os.getenv("S2MFLOW_DATA_DIR", "data")
GRIDGEN = os.path.join(DATA_DIR, "gridgen_1", "smcg_gridgen_1.min")

# Two parallel arcs (1,2), plus (2,3) and (1,3).
SMALL = """\
p min 3 4
n 1 10
n 3 -10
a 1 2 0 6 3
a 1 2 0 4 2
a 2 3 0 10 1
a 1 3 0 10 5
"""

SEQ = "p min 2 1\nn 1 5\nn 2 -5\na 1 2 0 5 1\n"

def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)

def _assert_unique_keys(md, num_arcs):
    """Critical property: no parallel arc overwrites another.

    The public 3-tuple keys are shared by MultiCommodityData and
    ParsedMulticommodityInstance. The position-keyed maps exist only on
    MultiCommodityData, so they are checked conditionally.
    """
    assert len(md.commodity_capacities) == num_arcs
    assert len(md.commodity_weights)    == num_arcs
    if hasattr(md, "capacities_by_arc"):
        assert len(md.capacities_by_arc) == num_arcs
        assert len(md.weights_by_arc)    == num_arcs

def test_small_parallel_parse(tmp_path):
    net = s2mflow.load_min_instance(_write(tmp_path, "s.min", SMALL))
    assert net.parallel is True
    assert net.num_parallel_arc_pairs == 1
    assert net.arcs == [(1, 2, 0), (1, 2, 1), (2, 3, 0), (1, 3, 0)]
    assert net.arc_indices[(1, 2)] == [0, 1]

def test_small_sequential_parse(tmp_path):
    net = s2mflow.load_min_instance(_write(tmp_path, "s.min", SEQ))
    assert net.parallel is False
    assert net.arcs == [(1, 2, 0)]
    assert all(e.index == 0 for e in net.edges)

def test_small_parallel_generate(tmp_path):
    net = s2mflow.load_min_instance(_write(tmp_path, "s.min", SMALL))
    md = s2mflow.generate_multi_commodity_data(net, 3, 0, seed=42)
    _assert_unique_keys(md, net.num_arcs)
    assert len(md.commodity_edges) == 3 * net.num_arcs

def test_small_parallel_round_trip(tmp_path):
    net = s2mflow.load_min_instance(_write(tmp_path, "s.min", SMALL))
    md = s2mflow.generate_multi_commodity_data(
        net, 3, 0,
        randomize_caps=True, cap_a=0.7, cap_b=1.0,
        randomize_costs=True, cost_a=0.8, cost_b=1.2,
        seed=42,
    )
    out = tmp_path / "p.mcfmin"
    s2mflow.save_multi_commodity_instance(str(out), net, md)
    ld = s2mflow.load_multi_commodity_instance(str(out))

    assert ld.parallel is True
    assert ld.edges == net.arcs
    _assert_unique_keys(ld, net.num_arcs)
    for i, (u, v, idx) in enumerate(ld.edges):
        assert ld.commodity_capacities[(u, v, idx)] == md.capacities_by_arc[i]
        assert ld.commodity_weights[(u, v, idx)]    == md.weights_by_arc[i]

@pytest.mark.skipif(not os.path.exists(GRIDGEN), reason="gridgen file not found")
def test_gridgen_round_trip(tmp_path):
    net = s2mflow.load_min_instance(GRIDGEN)
    assert net.parallel is True
    assert net.num_parallel_arc_pairs > 0

    md = s2mflow.generate_multi_commodity_data(net, 3, 0, seed=42)
    _assert_unique_keys(md, net.num_arcs)

    out = tmp_path / "g.mcfmin"
    s2mflow.save_multi_commodity_instance(str(out), net, md)
    ld = s2mflow.load_multi_commodity_instance(str(out))

    assert ld.parallel is True
    assert ld.edges == net.arcs
    _assert_unique_keys(ld, net.num_arcs)




