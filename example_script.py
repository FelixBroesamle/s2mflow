import pyomo.environ as pyo
import s2mflow

# 1. Load a multi-commodity benchmark instance from disk
mc = s2mflow.load_multi_commodity_instance("data/net_instance_1/netgen_1_5.mcfmin")

# 2. Initialize the Algebraic Optimization Model
model = pyo.ConcreteModel("MCMCF_Model")

# 3. Define Decision Variables with Edge-Wise Capacity Bounds: 0 <= x_e^k <= u_e^k
def commodity_edge_bounds(m, k, u, v):
    upper_bound = mc.commodity_capacities[(u, v)][k]
    return (0.0, float(upper_bound))

model.flow = pyo.Var(
    mc.commodity_edges,
    domain=pyo.NonNegativeReals,
    bounds=commodity_edge_bounds,
    name="x"
)

# 4. Objective Function: Minimize total routing cost over all commodities
model.obj = pyo.Objective(
    expr=sum(
        model.flow[k, u, v] * mc.commodity_weights[(u, v)][k]
        for (k, u, v) in mc.commodity_edges
    ),
    sense=pyo.minimize
)

# 5. Shared Mutual Capacity Constraints: sum_k (x_e^k) <= u_e
model.shared_caps = pyo.ConstraintList()
for i, edge in enumerate(mc.edges):  # loops through sequential arc structures
    u, v = edge[0], edge[1]
    shared_cap = mc.capacities[i]
    model.shared_caps.add(
        sum(model.flow[k, u, v] for k in range(mc.num_commodities)) <= shared_cap
    )

# 6. Flow Conservation Constraints (Local Balance System)
model.flow_balance = pyo.ConstraintList()
incoming, outgoing = s2mflow.get_adjacency_mapping(mc.nodes, mc.edges)

for k in range(mc.num_commodities):
    for node in mc.nodes:
        in_flow = sum(model.flow[k, u, node] for u in incoming.get(node, []))
        out_flow = sum(model.flow[k, node, v] for v in outgoing.get(node, []))
        
        # Pull demand vector or fallback to balanced zero
        demand = mc.commodity_supply_demand_data[node][k] if node in mc.commodity_supply_demand_data else 0.0
        
        model.flow_balance.add(out_flow - in_flow == demand)

# 7. Execute the Solver
print("[*] Passing algebraic matrix to HiGHS engine...")
solver = pyo.SolverFactory("highs")
results = solver.solve(model, tee=True)

print(f"[+] Optimal Objective Value: {pyo.value(model.obj)}")