"""
End-to-End Minimum-Cost Multicommodity Flow (MCMCF) Script.

Loads a baseline single-commodity `.min` file or a generated `.mcfmin` file,
builds the multicommodity flow model in Pyomo, and solves it with HiGHS.
"""
import os
import time
import s2mflow
import pyomo.environ as pyo


def solve_mcmcf_framework(
    nodes,
    base_edges,              # List[(tail, head, index)]
    commodity_edges,         # List[(k, tail, head, index)]
    num_commodities,
    capacities,              # List[int], aligned with base_edges
    commodity_capacities,    # Dict[(tail, head, index), List[int]]
    commodity_weights,       # Dict[(tail, head, index), List[int]]
    supply_demand_data,
    solver_name: str = "highs",
):
    print("[*] Constructing optimization model.")
    print(f"[*] Instance Profile: {len(nodes)} nodes, {len(base_edges)} arcs, {num_commodities} commodities.")

    model = pyo.ConcreteModel()

    # 2. Variables with per-commodity capacity bounds: 0 <= x_e^k <= u_e^k
    def commodity_edge_bounds(m, k, u, v, idx):
        return (0.0, float(commodity_capacities[(u, v, idx)][k]))

    model.flow = pyo.Var(
        commodity_edges,
        domain=pyo.NonNegativeReals,
        bounds=commodity_edge_bounds,
        name="x",
    )

    # 3. Objective
    model.obj = pyo.Objective(
        expr=sum(
            model.flow[k, u, v, idx] * commodity_weights[(u, v, idx)][k]
            for (k, u, v, idx) in commodity_edges
        ),
        sense=pyo.minimize,
    )

    # 4. Shared mutual capacity constraints: sum_k x_e^k <= u_e, one per arc
    model.shared_caps = pyo.ConstraintList()
    for i, (u, v, idx) in enumerate(base_edges):
        model.shared_caps.add(
            sum(model.flow[k, u, v, idx] for k in range(num_commodities))
            <= capacities[i]
        )

    # 5. Flow conservation — parallel-safe per-node arc lists
    in_arcs  = {n: [] for n in nodes}
    out_arcs = {n: [] for n in nodes}
    for arc in base_edges:
        u, v, _ = arc
        out_arcs[u].append(arc)
        in_arcs[v].append(arc)

    model.flow_balance = pyo.ConstraintList()
    for k in range(num_commodities):
        for node in nodes:
            in_flow  = sum(model.flow[k, u, v, idx] for (u, v, idx) in in_arcs[node])
            out_flow = sum(model.flow[k, u, v, idx] for (u, v, idx) in out_arcs[node])
            demand = supply_demand_data[node][k] if node in supply_demand_data else 0.0
            model.flow_balance.add(out_flow - in_flow == demand)

    # 6. Solve
    print("[*] Solver call")
    start_time = time.perf_counter()
    results = pyo.SolverFactory(solver_name).solve(model, tee=True)
    end_time = time.perf_counter()
    try:
        solver_runtime = results.solver.time
    except AttributeError:
        solver_runtime = end_time - start_time

    print(f"[+] Objective Value: {pyo.value(model.obj)}")
    print(f"[+] Solver Runtime: {solver_runtime} seconds")


def run_parsed_file_workflow(file_path: str, solver_name: str = "highs"):
    """Workflow 1: Solve a `.mcfmin` instance parsed from disk."""
    if not os.path.exists(file_path):
        print(f"[-] Parsed target file skip: {file_path} (does not exist).")
        return

    print(f"[*] Loading multicommodity instance: {file_path}")
    mc = s2mflow.load_multi_commodity_instance(file_path)

    solve_mcmcf_framework(
        nodes=mc.nodes,
        base_edges=mc.edges,
        commodity_edges=mc.commodity_edges,
        num_commodities=mc.num_commodities,
        capacities=mc.capacities,
        commodity_capacities=mc.commodity_capacities,
        commodity_weights=mc.commodity_weights,
        supply_demand_data=mc.commodity_supply_demand_data,
        solver_name=solver_name,
    )


def run_generation_and_solve_workflow(
    base_net_path: str,
    num_commodities: int = 3,
    solver_name: str = "highs",
):
    """Workflow 2: Generate a multi-commodity instance in memory and solve it."""
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

    solve_mcmcf_framework(
        nodes=net.nodes,
        base_edges=net.arcs,
        commodity_edges=mc.commodity_edges,
        num_commodities=mc.num_commodities,
        capacities=net.capacities,
        commodity_capacities=mc.commodity_capacities,
        commodity_weights=mc.commodity_weights,
        supply_demand_data=mc.supply_partition,
        solver_name=solver_name,
    )


if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    NUM_COMMODITIES = [2, 5, 10]
    SOLVER_NAMES = ["highs"]

    for solver_name in SOLVER_NAMES:
        for i in range(1, 5):
            NETWORK_MIN_FILE = os.path.join(BASE_DIR, "data", f"net_instance_{i}", f"netgen_{i}.min")
            if not os.path.exists(NETWORK_MIN_FILE):
                continue

            for k in NUM_COMMODITIES:
                print(f"=== MCMCF Optimization Pipeline (Solver = {solver_name}) ===")
                print(f"Network instance: netgen_{i}.min | Number of commodities: {k}")

                run_generation_and_solve_workflow(
                    NETWORK_MIN_FILE, num_commodities=k, solver_name=solver_name,
                )

                PARSED_MC_FILE = os.path.join(
                    BASE_DIR, "data", f"net_instance_{i}", f"netgen_{i}_{k}.mcfmin"
                )
                run_parsed_file_workflow(PARSED_MC_FILE, solver_name=solver_name)