# s2mflow


[![CI](https://github.com/FelixBroesamle/s2mflow/actions/workflows/ci.yml/badge.svg)](https://github.com/FelixBroesamle/s2mflow/actions/workflows/ci.yml)
[![Documentation](https://readthedocs.org/projects/s2mflow/badge/?version=latest)](https://s2mflow.readthedocs.io/en/latest/?badge=latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/pypi/pyversions/s2mflow.svg?color=blue)](https://pypi.org/project/s2mflow/)


**A high-performance meta-generation framework for lifting single-commodity flow instances into the multicommodity space.**

`s2mflow` is a Python library [PyPI](https://pypi.org/project/s2mflow/) with a high-speed Rust core (via PyO3) designed to transform single-commodity minimum-cost flow (MCF) instances into minimum-cost multicommodity flow (MCMCF) instances. It is built for researchers in Operations Research, Mathematical Optimization, and Network Optimization who need to generate reproducible, scalable test data.

The software package `s2mflow` is presented in [SoftwareX](https://www.sciencedirect.com/science/article/pii/S2352711026003651):
```text
Felix P. Broesamle, Stefan Nickel, s2mflow: A meta-generator for multicommodity flow instances, SoftwareX, Volume 35, 2026, 102874, ISSN 2352-7110, https://doi.org/10.1016/j.softx.2026.102874.
```

The theoretical meta-generation framework and mathematical foundations are introduced in:
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

### Verifying the Installation

After building from source, you can verify that both the Rust core and the Python bindings are functioning correctly by running the test suites:

```bash
# Run the Rust test-suite
cargo test

# Run the Python test suite
poetry run pytest
# To run the Python tests in parallel, use:
poetry run pytest -n auto
```

### Running the Example Workflows

The repository includes demo scripts and datasets to help you verify the end-to-end workflow after installation. Sample network instances are provided in the `data/` directory. Example scripts are locatet in the `examples` directory.

```bash
# Execute the core s2mflow multicommodity instance generation workflow
poetry run python examples/demo.py

# Execute the below Pyomo + HiGHS optimization workflow
poetry run python examples/solve_instance_pyomo.py
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
model = pyo.ConcreteModel("MCMCF")

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
for i, (u, v) in enumerate(mc.edges):
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
model = grb.Model("MCMCF")

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

## Benchmarks and Scaling

The following benchmarks were executed on an Intel Core Ultra 7 255U (32 GB RAM) using the standard `NETGEN-SR` instance family (LEMON graph library). The benchmark script and benchmark data are available in the directories `examples/benchmark.py` and `data/`.

**Benchmark: Standard vs. Randomized Parameter Generation**

* **Standard:** Spread partitioning with shared commodity capacities and costs.  
* **Randomized:** Spread partitioning with randomized capacities and costs for every individual commodity-arc pair.

### Benchmark Metrics

* **Base Topology:** Instance, Nodes, Arcs, Commodities (K), Sources (Srcs), Demands (Dmds), and Total Demand.
* **Pipeline Phases:** Min-cost flow base load (`Load Min`), parameter generation (`Gen`), MCF writer (`Write`), MCF re-load (`Load MCF`), and total execution time (`Total`).

| Instance | Nodes | Arcs | K | Srcs | Dmds | Tot Demand | Load Min (s) | Gen: Std / Rand (s) | Write: Std / Rand (s) | Load MCF: Std / Rand (s) | Total: Std / Rand (s) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `netgen_sr_08a` | 256 | 4,096 | 2 | 16 | 16 | 16,000.0 | 0.0014 | 0.0020 / 0.0028 | 0.0019 / 0.0024 | 0.0161 / 0.0117 | 0.0214 / 0.0184 |
| `netgen_sr_08a` | 256 | 4,096 | 5 | 16 | 16 | 16,000.0 | 0.0014 | 0.0030 / 0.0031 | 0.0019 / 0.0049 | 0.0158 / 0.0190 | 0.0221 / 0.0284 |
| `netgen_sr_08a` | 256 | 4,096 | 10 | 16 | 16 | 16,000.0 | 0.0014 | 0.0039 / 0.0048 | 0.0049 / 0.0050 | 0.0168 / 0.0135 | 0.0271 / 0.0246 |
| `netgen_sr_08a` | 256 | 4,096 | 20 | 16 | 16 | 16,000.0 | 0.0014 | 0.0061 / 0.0068 | 0.0022 / 0.0096 | 0.0111 / 0.0173 | 0.0208 / 0.0350 |
| `netgen_sr_08a` | 256 | 4,096 | 30 | 16 | 16 | 16,000.0 | 0.0014 | 0.0078 / 0.0101 | 0.0031 / 0.0131 | 0.0192 / 0.0150 | 0.0315 / 0.0396 |
| `netgen_sr_08a` | 256 | 4,096 | 50 | 16 | 16 | 16,000.0 | 0.0014 | 0.0127 / 0.0142 | 0.0026 / 0.0217 | 0.0181 / 0.0216 | 0.0348 / 0.0589 |
| `netgen_sr_10a` | 1,024 | 32,768 | 2 | 32 | 32 | 32,000.0 | 0.0079 | 0.0195 / 0.0244 | 0.0128 / 0.0180 | 0.0318 / 0.0298 | 0.0720 / 0.0801 |
| `netgen_sr_10a` | 1,024 | 32,768 | 5 | 32 | 32 | 32,000.0 | 0.0079 | 0.0277 / 0.0349 | 0.0132 / 0.0239 | 0.0406 / 0.0390 | 0.0894 / 0.1057 |
| `netgen_sr_10a` | 1,024 | 32,768 | 10 | 32 | 32 | 32,000.0 | 0.0079 | 0.0487 / 0.0504 | 0.0190 / 0.0407 | 0.0389 / 0.0465 | 0.1145 / 0.1455 |
| `netgen_sr_10a` | 1,024 | 32,768 | 20 | 32 | 32 | 32,000.0 | 0.0079 | 0.0861 / 0.0759 | 0.0164 / 0.0733 | 0.0365 / 0.0639 | 0.1470 / 0.2211 |
| `netgen_sr_10a` | 1,024 | 32,768 | 30 | 32 | 32 | 32,000.0 | 0.0079 | 0.1130 / 0.1267 | 0.0160 / 0.0949 | 0.0412 / 0.0830 | 0.1781 / 0.3126 |
| `netgen_sr_10a` | 1,024 | 32,768 | 50 | 32 | 32 | 32,000.0 | 0.0079 | 0.1936 / 0.1788 | 0.0164 / 0.1651 | 0.0477 / 0.1051 | 0.2656 / 0.4570 |
| `netgen_sr_11a` | 2,048 | 92,682 | 2 | 45 | 45 | 45,000.0 | 0.0288 | 0.0617 / 0.0627 | 0.0388 / 0.0399 | 0.0627 / 0.0793 | 0.1921 / 0.2107 |
| `netgen_sr_11a` | 2,048 | 92,682 | 5 | 45 | 45 | 45,000.0 | 0.0288 | 0.0872 / 0.0891 | 0.0390 / 0.0639 | 0.0755 / 0.0892 | 0.2305 / 0.2710 |
| `netgen_sr_11a` | 2,048 | 92,682 | 10 | 45 | 45 | 45,000.0 | 0.0288 | 0.1392 / 0.1526 | 0.0433 / 0.1123 | 0.0727 / 0.1201 | 0.2840 / 0.4138 |
| `netgen_sr_11a` | 2,048 | 92,682 | 20 | 45 | 45 | 45,000.0 | 0.0288 | 0.2487 / 0.2565 | 0.0490 / 0.2050 | 0.0818 / 0.1656 | 0.4084 / 0.6559 |
| `netgen_sr_11a` | 2,048 | 92,682 | 30 | 45 | 45 | 45,000.0 | 0.0288 | 0.3355 / 0.3752 | 0.0481 / 0.2769 | 0.0931 / 0.2092 | 0.5056 / 0.8901 |
| `netgen_sr_11a` | 2,048 | 92,682 | 50 | 45 | 45 | 45,000.0 | 0.0288 | 0.5252 / 0.5722 | 0.0486 / 0.4520 | 0.0944 / 0.2797 | 0.6969 / 1.3328 |
| `netgen_sr_12a` | 4,096 | 262,144 | 2 | 64 | 64 | 64,000.0 | 0.0717 | 0.1810 / 0.1875 | 0.0990 / 0.1154 | 0.1753 / 0.1833 | 0.5270 / 0.5579 |
| `netgen_sr_12a` | 4,096 | 262,144 | 5 | 64 | 64 | 64,000.0 | 0.0717 | 0.2492 / 0.3510 | 0.1025 / 0.2484 | 0.2692 / 0.2558 | 0.6926 / 0.9268 |
| `netgen_sr_12a` | 4,096 | 262,144 | 10 | 64 | 64 | 64,000.0 | 0.0717 | 0.4230 / 0.4720 | 0.1147 / 0.3328 | 0.1941 / 0.4041 | 0.8035 / 1.2806 |
| `netgen_sr_12a` | 4,096 | 262,144 | 20 | 64 | 64 | 64,000.0 | 0.0717 | 0.7596 / 0.7833 | 0.1311 / 0.5724 | 0.2219 / 0.4668 | 1.1843 / 1.8942 |
| `netgen_sr_12a` | 4,096 | 262,144 | 30 | 64 | 64 | 64,000.0 | 0.0717 | 1.0187 / 1.0748 | 0.1365 / 0.8125 | 0.2406 / 0.5733 | 1.4675 / 2.5322 |
| `netgen_sr_12a` | 4,096 | 262,144 | 50 | 64 | 64 | 64,000.0 | 0.0717 | 1.6150 / 1.6995 | 0.1344 / 1.3241 | 0.2645 / 0.7686 | 2.0854 / 3.8638 |
| `netgen_sr_13a` | 8,192 | 741,455 | 2 | 91 | 91 | 91,000.0 | 0.1984 | 0.5413 / 0.6616 | 0.2873 / 0.3348 | 0.5059 / 0.5288 | 1.5329 / 1.7236 |
| `netgen_sr_13a` | 8,192 | 741,455 | 5 | 91 | 91 | 91,000.0 | 0.1984 | 0.7915 / 0.8514 | 0.2969 / 0.5204 | 0.4610 / 0.6832 | 1.7477 / 2.2534 |
| `netgen_sr_13a` | 8,192 | 741,455 | 10 | 91 | 91 | 91,000.0 | 0.1984 | 1.3138 / 1.4663 | 0.3430 / 0.8733 | 0.6083 / 1.0841 | 2.4635 / 3.6221 |
| `netgen_sr_13a` | 8,192 | 741,455 | 20 | 91 | 91 | 91,000.0 | 0.1984 | 2.3683 / 2.4099 | 0.3825 / 1.4801 | 0.6710 / 1.7515 | 3.6202 / 5.8399 |
| `netgen_sr_13a` | 8,192 | 741,455 | 30 | 91 | 91 | 91,000.0 | 0.1984 | 3.1107 / 3.3099 | 0.4015 / 2.0738 | 0.7936 / 1.9420 | 4.5042 / 7.5241 |
| `netgen_sr_13a` | 8,192 | 741,455 | 50 | 91 | 91 | 91,000.0 | 0.1984 | 4.9060 / 5.2603 | 0.4100 / 3.3010 | 0.8825 / 2.5859 | 6.3968 / 11.3457 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 2 | 128 | 128 | 128,000.0 | 0.8777 | 1.9554 / 2.9611 | 0.8183 / 0.9636 | 2.3140 / 2.0434 | 5.9653 / 6.8458 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 5 | 128 | 128 | 128,000.0 | 0.8777 | 4.2976 / 4.4220 | 0.8563 / 1.5197 | 1.6861 / 2.8761 | 7.7177 / 9.6956 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 10 | 128 | 128 | 128,000.0 | 0.8777 | 7.1258 / 8.8457 | 0.9693 / 2.4662 | 3.6271 / 4.8378 | 12.5999 / 17.0274 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 20 | 128 | 128 | 128,000.0 | 0.8777 | 12.5907 / 12.2959 | 1.1096 / 4.6455 | 2.9332 / 5.2400 | 17.5112 / 23.0591 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 30 | 128 | 128 | 128,000.0 | 0.8777 | 13.9071 / 15.4077 | 1.1207 / 6.2683 | 2.3871 / 4.6295 | 18.2926 / 27.1831 |
| `netgen_sr_14a` | 16,384 | 2,097,152 | 50 | 128 | 128 | 128,000.0 | 0.8777 | 20.8690 / **24.6117** | 1.1872 / 10.1748 | 2.7607 / 7.7355 | 25.6946 / **43.3997** |

*Note: In the largest randomized case (`netgen_sr_14a`, $K=50$), the Rust engine generates over 104 million independent random parameters. The generation phase remains highly performant (+3.7 seconds), while the total pipeline time increases primarily due to the physical disk I/O required to write and load the expanded (full) `.mcfmin` file. All benchmark instances and generation configurations are available in the [LEMON Graph Library](https://lemon.cs.elte.hu/trac/lemon/wiki/MinCostFlowData).*

## Citing

If you use `s2mflow` in your research, please use the following preferred citation:
```text
@article{BroesamleNickel:s2mflow,
  title   = {s2mflow: A meta-generator for multicommodity flow instances},
  author  = {Broesamle, Felix P. and Nickel, Stefan},
  journal = {SoftwareX},
  volume  = {35},
  pages   = {102874},
  year    = {2026},
  issn    = {2352-7110},
  doi     = {10.1016/j.softx.2026.102874},
  url     = {https://doi.org/10.1016/j.softx.2026.102874}
}
```

If you refer to the meta-generation framework and mathematical foundations, please cite the following paper:
```text
@misc{BroesamleNickel:SMCG,
  author       = {Broesamle, Felix P. and Nickel, Stefan},
  title        = {On the Single-Multi-Commodity Gap: Lifting Single- to Multicommodity Flow Instances},
  year         = {2026},
  howpublished = {Optimization Online},
  note         = {Preprint. Available at https://optimization-online.org/?p=34287.},
}
```

## Resources

- **Documentation**: [s2mflow.readthedocs.io](https://s2mflow.readthedocs.io/en/latest/)
- **PyPI Package**: [pypi.org/project/s2mflow](https://pypi.org/project/s2mflow/)

## License

Distributed under the MIT License. See `LICENSE` for more information.