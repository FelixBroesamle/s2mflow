"""
End-to-End Minimum-Cost Multicommodity Flow (MCMCF) Script via gurobipy.

Loads a baseline `.min` file or a generated `.mcfmin` file, builds the
multicommodity flow model in gurobipy, and solves it.
"""
import os
import time
import s2mflow
import gurobipy as grb


def solve_mcmcf_framework_gurobi(
    nodes,
    base_edges,              # List[(tail, head, index)]
    commodity_edges,         # List[(k, tail, head, index)]
    num_commodities,
    capacities,
    commodity_capacities,    # Dict[(tail, head, index), List[int]]
    commodity_weights,       # Dict[(tail, head, index), List[int]]
    supply_demand_data,
    method: int = 1,
):
    print("[*] Constructing Gurobi optimization model.")
    print(f"[*] Instance Profile: {len(nodes)} nodes, {len(base_edges)} arcs, {num_commodities} commodities.")

    model = grb.Model("MCMCF_Direct")
    model.setParam("Method", method)

    # 2. Variables with per-commodity capacity bounds
    upper_bounds = [
        commodity_capacities[(u, v, idx)][k]
        for (k, u, v, idx) in commodity_edges
    ]
    flow = model.addVars(
        commodity_edges,
        lb=0.0,
        ub=upper_bounds,
        vtype=grb.GRB.CONTINUOUS,
        name="x",
    )

    # 3. Objective
    model.setObjective(
        grb.quicksum(
            flow[k, u, v, idx] * commodity_weights[(u, v, idx)][k]
            for (k, u, v, idx) in commodity_edges
        ),
        sense=grb.GRB.MINIMIZE,
    )

    # 4. Shared mutual capacity — one constraint per arc
    model.addConstrs(
        (
            grb.quicksum(flow[k, u, v, idx] for k in range(num_commodities)) <= capacities[i]
            for i, (u, v, idx) in enumerate(base_edges)
        ),
        name="Shared_Cap",
    )

    # 5. Flow conservation — parallel-safe per-node arc lists
    in_arcs, out_arcs = s2mflow.get_incidence_mapping(nodes, base_edges)

    for k in range(num_commodities):
        for node in nodes:
            in_flow  = grb.quicksum(flow[k, u, v, idx] for (u, v, idx) in in_arcs[node])
            out_flow = grb.quicksum(flow[k, u, v, idx] for (u, v, idx) in out_arcs[node])
            demand = supply_demand_data[node][k] if node in supply_demand_data else 0.0
            model.addConstr(out_flow - in_flow == demand, name=f"balance_{k}_{node}")

    # 6. Solve
    print(f"[*] Gurobi: solve model (Method = {method})")
    start_time = time.perf_counter()
    model.optimize()
    end_time = time.perf_counter()
    solver_runtime = model.Runtime if model.Status == grb.GRB.OPTIMAL else end_time - start_time

    if model.Status == grb.GRB.OPTIMAL:
        print(f"[+] Objective Value: {model.ObjVal}")
        print(f"[+] Solver Runtime: {solver_runtime:.6f} seconds\n")
    else:
        print(f"[-] Solver encountered termination code: {model.Status}\n")


def run_parsed_file_workflow(file_path: str, method: int = 1):
    if not os.path.exists(file_path):
        print(f"[-] Target file skip: {file_path} (does not exist).")
        return

    print(f"[*] Loading multicommodity instance: {file_path}")
    mc = s2mflow.load_multi_commodity_instance(file_path)

    solve_mcmcf_framework_gurobi(
        nodes=mc.nodes,
        base_edges=mc.edges,
        commodity_edges=mc.commodity_edges,
        num_commodities=mc.num_commodities,
        capacities=mc.capacities,
        commodity_capacities=mc.commodity_capacities,
        commodity_weights=mc.commodity_weights,
        supply_demand_data=mc.commodity_supply_demand_data,
        method=method,
    )


def run_generation_and_solve_workflow(
    base_net_path: str,
    num_commodities: int = 3,
    method: int = 1,
):
    if not os.path.exists(base_net_path):
        raise FileNotFoundError(f"Base network instance not found: {base_net_path}")

    print(f"[*] Loading baseline single-commodity network: {base_net_path}")
    net = s2mflow.load_min_instance(base_net_path)

    print("[*] Generate multicommodity data via s2mflow ...")
    mc = s2mflow.generate_multi_commodity_data(
        instance=net,
        num_commodities=num_commodities,
        method=0,
        randomize_caps=False,
        randomize_costs=False,
        seed=512,
    )

    solve_mcmcf_framework_gurobi(
        nodes=net.nodes,
        base_edges=net.arcs,
        commodity_edges=mc.commodity_edges,
        num_commodities=mc.num_commodities,
        capacities=net.capacities,
        commodity_capacities=mc.commodity_capacities,
        commodity_weights=mc.commodity_weights,
        supply_demand_data=mc.supply_partition,
        method=method,
    )


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    NUM_COMMODITIES = [2, 5, 10]
    METHODS = [1]

    for method in METHODS:
        for i in range(1, 5):
            NETWORK_MIN_FILE = os.path.join(BASE_DIR, "data", f"net_instance_{i}", f"netgen_{i}.min")
            if not os.path.exists(NETWORK_MIN_FILE):
                continue

            for k in NUM_COMMODITIES:
                print(f"=== Gurobi MCMCF Pipeline (Method = {method}) ===")
                print(f"Network instance: netgen_{i}.min | Commodities: {k}")

                PARSED_MC_FILE = os.path.join(
                    BASE_DIR, "data", f"net_instance_{i}", f"netgen_{i}_{k}.mcfmin"
                )

                run_generation_and_solve_workflow(
                    base_net_path=NETWORK_MIN_FILE, num_commodities=k, method=method,
                )
                run_parsed_file_workflow(PARSED_MC_FILE, method=method)