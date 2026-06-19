# s2mflow


[![CI](https://github.com/FelixBroesamle/s2mflow/actions/workflows/ci.yml/badge.svg)](https://github.com/FelixBroesamle/s2mflow/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/s2mflow/badge/?version=latest)](https://s2mflow.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/s2mflow.svg?color=blue)](https://pypi.org/project/s2mflow/)


**A high-performance meta-generation framework for lifting single-commodity flow instances into the multicommodity space.**

`s2mflow` is a Python library [PyPI](https://pypi.org/project/s2mflow/) with a high-speed Rust core (via PyO3) designed to transform single-commodity minimum-cost flow (MCF) instances into minimum-cost multicommodity flow (MCMCF) instances. It is built for researchers in Operations Research, Mathematical Optimization, and Network Optimization who need to generate reproducible, scalable test data.

`s2mflow` implements and extends the meta-generation framework introduced in:
```text
Felix P. Broesamle and Stefan Nickel. 2026. "On the Single-Multi-Commodity Gap: Lifting Single- to Multicommodity Flow Instances". Optimization Online. Preprint. Available at https://optimization-online.org/?p=34287.
```

## Key Features

- **High Performance**: Core logic implemented in Rust for zero-overhead data handling.
- **DIMACS Compatible**: Load standard `.min` single-commodity files.
- **Custom MCMCF Format**: Introduces the `.mcfmin` format for standardized multicommodity data storage.
- **Supply Partitioning Methods**:
    - `uniform`: Equal distribution of supply and demand across commodities.
    - `spread`: Randomized, heterogeneous distribution of supply and demand across commodities.
- **Randomizing Capacities and Costs**: Functionality for generating randomized commodity-specific capacities and costs for each arc.
- **Network Utilities**: Support for identifying incoming and outgoing neighboring nodes.

## Installation

### Standard Installation

`s2mflow` provides pre-compiled binary wheels for major platforms. Install directly via `pip` or `poetry`:
```bash
pip install s2mflow
# or via poetry
poetry add s2mflow
```

### Building from Source
```bash
git clone https://github.com/FelixBroesamle/s2mflow.git
cd s2mflow
poetry install -vvv
poetry run maturin develop --release
```

### Running Mathematical Models

To run the below mathematical modeling examples included in this repository out-of-the-box, install the optional solver dependencies:
```bash
poetry install --extras solver
```

## Quick Start

The following snippet illustrates an end-to-end workflow: parsing a standard single-commodity DIMACS `.min` network file, lifting it into a 3-commodity space with high commodity-demand heterogeneity (`Spread`), and exporting the output. It also demonstrates how to bypass file formats entirely for direct integration.
```python
import s2mflow

# Input file example contents:
# p min 2 1         (2 nodes, 1 arc)
# n 1 10            (Node 1: supply of 10)
# n 2-10            (Node 2: demand of 10)
# a 1 2 0 10 9      (Arc from 1 to 2, min_cap=0, max_cap=10, cost=9)

# 1. Load a single-commodity network (DIMACS .min format)
network = s2mflow.load_min_instance("input.min")

# 2. Generate multicommodity data for 3 commodities
# is_uniform=False activates the stochastic 'Spread' method
mc_data = s2mflow.generate_multi_commodity_data(
    instance=network,
    num_commodities=3,
    is_uniform=False,
    randomize_caps=False,
    randomize_costs=False,
    seed=512,
)

# 3. Save as a multi-commodity instance (.mcfmin format)
s2mflow.save_multi_commodity_instance("output.mcfmin", network, mc_data)

# Output file (.mcfmin format)
# p min 2 1 3 0 0 512       (3 commodities, randomize_caps = False (0), randomize_costs = False (0) seed = 512)
# n 1 10 2 5 3      (Supply of 10 split into supplies: 2, 5, 3)
# n 2-10-2-5-3      (Demand of-10 split into demands: -2,-5,-3)
# a 1 2 0 10 10 9

# 4. Load multicommodity instance back into memory
loaded_mc_data = s2mflow.load_multi_commodity_instance("output.mcfmin")

# 5. Direct usage bypassing formal file formats
data = {1: 126, 2:-126}
spread_multi_data = s2mflow.split_supplies_spread(data, num_commodities=5, seed=512)
# spread_multi_data = {1: [6, 24, 23, 12, 61], 2: [-6,-24,-23,-12,-61]}

uniform_multi_data = s2mflow.split_supplies_uniform(data, num_commodities=5)
# uniform_multi_data = {1: [25, 26, 25, 25, 25], 2: [-25,-26,-25,-25,-25]}
```

## The Extended `.mcfmin` Format

The library uses a natural extension of the DIMACS `.min` format to support multiple commodities:

- **Problem Line**: `p min <num_nodes> <num_edges> <num_commodities> <randomize_caps> <randomize_costs> <is_uniform> <seed = 0>`.
    - `seed`: relevant if `is_uniform = 0` (Spread method) or if randomization of commodity-specific capacities or costs is enabled (`randomize_caps = 1` or `randomize_costs = 1`).
- **Node Line**: `n <node_id> <total_demand> <demand_com_1> <demand_com_2> ... <demand_com_K>`.
- **Arc Line**: Depending on the randomization flags `(randomize_caps, randomize_costs)`:
    - Default `(0, 0)`: `a <from> <to> <low> <cap_total> <cap_total> <cost>`.
    - Commodity-specific capacities `(1, 0)`: `a <from> <to> <low> <cap_total> <cap_1> ... <cap_K> <cost>`.
    - Commodity-specific costs `(0, 1)`: `a <from> <to> <low> <cap_total> <cap_total> <cost_1> ... <cost_K>`.
    - Commodity-specific capacities and costs `(1, 1)`: `a <from> <to> <low> <cap_total> <cap_1> ... <cap_K> <cost_1> ... <cost_K>`.

### Examples for the .mcfmin Format

Below, we illustrate how the file structure shifts when applying different generation configurations.

#### Based Single-Commodity Instance (input.min)
```python
# c Base single-commodity instance (input.min)
# p min 4 5
# n 1 17
# n 4 -17
# a 1 2 0 10 10
# a 1 3 0 15 5
# a 2 4 0 10 10
# a 3 2 0 5 20
# a 3 4 0 15 4
```

#### Strategy 1: Uniform Partitioning
This strategy distributes the nodal demands as evenly as possible across the 4 commodities.

```python
uniform_mc_data = s2mflow.generate_multi_commodity_data(instance=network, num_commodities=4, is_uniform=True, randomize_caps=False, randomize_costs=False)

s2mflow.save_multi_commodity_instance("uniform.mcfmin", network, uniform_mc_data)

# --- Output File Contents (uniform.mcfmin) ---
# c Multicommodity flow generated by s2mflow
# p min 4 5 4 0 0 1 0
# n 1 17 5 4 4 4
# n 4 -17 -5 -4 -4 -4
# a 1 2 0 10 10 10
# a 1 3 0 15 15 5
# a 2 4 0 10 10 10
# a 3 2 0 5 5 20
# a 3 4 0 15 15 4
```

#### Strategy 2: Spread Partitioning with Randomized Capacities and Costs

This strategy generates high commodity-demand heterogeneity and simultaneously applies uniform noise to individual commodity capacities and arc costs.

```python
spread_rand_caps_costs_mc_data = s2mflow.generate_multi_commodity_data(
    instance=network, num_commodities=4, is_uniform=False,
    randomize_caps=True, cap_a=0.6, cap_b=1.0,
    randomize_costs=True, cost_a=0.5, cost_b=2.0,
    seed=42,
)
s2mflow.save_multi_commodity_instance("spread_full.mcfmin", network, spread_rand_caps_costs_mc_data)

# --- Output File Contents (spread_full.mcfmin) ---
# c Multicommodity flow generated by s2mflow
# p min 4 5 4 1 1 0 42
# n 1 17 4 6 1 6
# n 4 -17 -4 -6 -1 -6
# a 1 2 0 10 9 8 8 10 13 15 6 17
# a 1 3 0 15 10 13 10 11 4 10 6 7
# a 2 4 0 10 9 9 8 7 6 6 18 13
# a 3 2 0 5 4 4 5 5 21 34 23 23
# a 3 4 0 15 15 11 12 12 8 6 6 3
```

(For demonstrations of isolated randomization configurations, see the `examples/demo.py` file).

## End-to-End Optimization Workflows

The instance attributes exposed by `s2mflow` integrate seamlessly into algebraic modeling languages and solvers.

### Workflow 1: File-Based Parsing with Pyomo & HiGHS (Open-Source)

This workflow loads a serialized .mcfmin file, builds a mathematical program in Pyomo, and solves it using HiGHS.

```python
import pyomo.environ as pyo
import s2mflow

# 1. Load multi-commodity benchmark instance
mc = s2mflow.load_multi_commodity_instance("spread_full.mcfmin")

# 2. Initialize Model
model = pyo.ConcreteModel("MCMCF_Model")

# 3. Decision Variables: 0 <= x_e^k <= u_e^k
def commodity_edge_bounds(m, k, u, v):
    upper_bound = mc.commodity_capacities[(u, v)][k]
    return (0.0, float(upper_bound))

model.flow = pyo.Var(
    mc.commodity_edges,
    domain=pyo.NonNegativeReals,
    bounds=commodity_edge_bounds,
    name="x"
)

# 4. Objective: Minimize total routing cost
model.obj = pyo.Objective(
    expr=sum(
        model.flow[k, u, v] * mc.commodity_weights[(u, v)][k]
        for (k, u, v) in mc.commodity_edges
    ),
    sense=pyo.minimize
)

# 5. Shared Mutual Capacity Constraints
model.shared_caps = pyo.ConstraintList()
for i, edge in enumerate(mc.edges):
    u, v = edge[0], edge[1]
    model.shared_caps.add(
        sum(model.flow[k, u, v] for k in range(mc.num_commodities)) <= mc.capacities[i]
    )

# 6. Flow Conservation Constraints
model.flow_balance = pyo.ConstraintList()
incoming, outgoing = s2mflow.get_adjacency_mapping(mc.nodes, mc.edges)

for k in range(mc.num_commodities):
    for node in mc.nodes:
        in_flow = sum(model.flow[k, u, node] for u in incoming.get(node, []))
        out_flow = sum(model.flow[k, node, v] for v in outgoing.get(node, []))
        
        demand = mc.commodity_supply_demand_data[node][k] if node in mc.commodity_supply_demand_data else 0.0
        model.flow_balance.add(out_flow - in_flow == demand)

# 7. Solve
solver = pyo.SolverFactory("highs")
results = solver.solve(model, tee=True)
print(f"[+] Optimal Objective Value: {pyo.value(model.obj)}")
```

We have provided in `examples/solve_instance_pyomo.py` a complete workflow / pipeline for running examples on some provided network instances (see `data/`).

### Workflow 2: In-Memory Generation with Gurobi (Commercial Solver)

This example bypasses a file serialization entirely, generating the multicommodity partitions dynamically in-memory. The mathematical model is solved with the `gurobipy` API for the commercial solver Gurobi (Requires a valid Gurobi license for instances of a certain size).

```python
import gurobipy as grb
import s2mflow

# 1. Load baseline and generate data in-memory
net = s2mflow.load_min_instance("input.min")
mc_data = s2mflow.generate_multi_commodity_data(net, num_commodities=3, is_uniform=False, seed=512)

# 2. Initialize Gurobi Model
model = grb.Model("MCMCF_InMemory")

# 3. Decision Variables
upper_bounds = [mc_data.commodity_capacities[(u, v)][k] for (k, u, v) in mc_data.commodity_edges]
flow = model.addVars(
    mc_data.commodity_edges, 
    lb=0.0, 
    ub=upper_bounds, 
    vtype=grb.GRB.CONTINUOUS, 
    name="x"
)

# 4. Objective Function
model.setObjective(
    grb.quicksum(flow[k, u, v] * mc_data.commodity_weights[(u, v)][k] for (k, u, v) in mc_data.commodity_edges),
    sense=grb.GRB.MINIMIZE
)

# 5. Shared Mutual Capacity Constraints
model.addConstrs(
    (
        grb.quicksum(flow[k, u, v] for k in range(mc_data.num_commodities)) <= net.capacities[i]
        for i, (u, v) in enumerate(net.arcs)
    ), name="Shared_Cap"
)

# 6. Flow Conservation Constraints
incoming, outgoing = s2mflow.get_adjacency_mapping(net.nodes, net.arcs)
for k in range(mc_data.num_commodities):
    for node in net.nodes:
        in_flow = grb.quicksum(flow[k, u, node] for u in incoming.get(node, []))
        out_flow = grb.quicksum(flow[k, node, v] for v in outgoing.get(node, []))
        
        demand = mc_data.supply_partition[node][k] if node in mc_data.supply_partition else 0.0
        model.addConstr(
            out_flow - in_flow == demand, 
            name=f"balance_{k}_{node}"
        )

# 7. Solve
model.optimize()
if model.Status == GRB.OPTIMAL:
    print(f"[+] Optimal Objective Value: {model.ObjVal}")
```

We have provided in `examples/solve_instance_gurobi.py` a complete workflow / pipeline for running examples on some provided network instances (see `data/`).

## Citing

If you use `s2mflow` in your research, please use the following preferred citation for the framework:
```text
@misc{BroesamleNickel:SMCG,
    author = {Broesamle, Felix P. and Nickel, Stefan},
    title = {On the Single-Multi-Commodity Gap: Lifting Single- to Multicommodity Flow Instances},
    year = {2026},
    howpublished = {Optimization Online},
    note = {Preprint. Available at \url{https://optimization-online.org/?p=34287}},
    url = {https://optimization-online.org/?p=34287},
}
```

To cite `s2mflow` specifically in your research, please cite the software:
```text
@software{s2mflow2026,
  author = {Broesamle, Felix P. and Nickel, Stefan},
  title = {s2mflow: A Meta-generator for Multicommodity Flow Instances},
  year = {2026},
  url = {https://github.com/FelixBroesamle/s2mflow}
}
```

## Resources

- **Documentation**: [s2mflow.readthedocs.io](https://s2mflow.readthedocs.io/en/latest/)
- **PyPI Package**: [pypi.org/project/s2mflow](https://pypi.org/project/s2mflow/)

## License

Distributed under the MIT License. See `LICENSE` for more information.