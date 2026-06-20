# End-to-End Optimization Workflows

The instance attributes exposed by `s2mflow` integrate seamlessly into algebraic modeling languages and solvers. By utilizing unified, tuple-keyed dictionary structures, you can map the generated multicommodity data directly to solver variables and constraints.

We have provided complete, runnable workflows in the `examples/` directory of the repository. Below are the primary integration workflows.

## 1. Data Generation & Serialization Pipeline

Before executing optimization routines, you must generate the multicommodity benchmark data. This workflow demonstrates how to load a standard DIMACS single-commodity network, apply a generation strategy (such as the heterogeneous `Spread` method with added capacity/cost noise), and serialize the output to disk for reproducible experimentation.

```python
import s2mflow

# 1. Load a baseline single-commodity network (DIMACS .min format)
network = s2mflow.load_min_instance("data/input.min")

# 2. Lift into the multicommodity space
# Using the 'Spread' strategy with randomized noise bounds
mc_data = s2mflow.generate_multi_commodity_data(
    instance=network,
    num_commodities=4,
    is_uniform=False,       # Activates stochastic Spread partitioning
    randomize_caps=True, 
    cap_a=0.6, 
    cap_b=1.0,
    randomize_costs=True, 
    cost_a=0.5, 
    cost_b=2.0,
    seed=42,
)

# 3. Serialize to disk for reproducible benchmarking
output_filename = "data/spread_full.mcfmin"
s2mflow.save_multi_commodity_instance(output_filename, network, mc_data)
print(f"Successfully generated and saved to {output_filename}")

# 4. Verify serialization by loading the instance back into memory
loaded_mc_data = s2mflow.load_multi_commodity_instance(output_filename)
print(f"Loaded {loaded_mc_data.num_commodities} commodities from disk.")

```

## 2. File-Based Parsing with Pyomo & HiGHS (Open-Source)

This workflow loads a serialized `.mcfmin` file from disk, builds a mathematical program using the Pyomo algebraic modeling language, and solves it using the open-source HiGHS solver.

```python
import pyomo.environ as pyo
import s2mflow

# 1. Load multi-commodity benchmark instance
mc = s2mflow.load_multi_commodity_instance("data/spread_full.mcfmin")

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

## 3. In-Memory Generation with Gurobi (Commercial Solver)

For researchers solving large-scale programs, `s2mflow` interfaces smoothly with the `gurobipy` API for the commercial solver Gurobi. This example bypasses file serialization entirely, generating the multicommodity partitions dynamically in-memory and passing them directly to the solver matrix. 

*(Note: Executing this script for large instances requires a valid Gurobi license).*

```python
import gurobipy as grb
import s2mflow

# 1. Load baseline and generate data in-memory
net = s2mflow.load_min_instance("data/input.min")
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
if model.Status == grb.GRB.OPTIMAL:
    print(f"[+] Optimal Objective Value: {model.ObjVal}")

```
