from .s2mflow import (
    load_min_instance,
    split_supplies_uniform,
    split_supplies_spread,
    split_supplies_beta_binomial,
    compute_commodity_demand_heterogeneity,
    generate_multi_commodity_data,
    save_multi_commodity_instance,
    load_multi_commodity_instance,
    get_adjacency_mapping,
    Edge,
    NetworkInstance,
    MultiCommoditySupplies,
    MultiCommodityData,
    ParsedMulticommodityInstance,
)

Edge.__doc__ = """
Represents a single directed arc within the network.

Every arc is uniquely identified by ``(tail, head, index)`` where ``index``
is the 0-based position of the arc among arcs sharing ``(tail, head)``.
For instances without parallel arcs, ``index`` is always 

Attributes:
    tail (int): The source node ID of the edge.
    head (int): The destination node ID of the edge.
    low (int): The lower bound of flow permitted on the edge.
    up (int): The upper bound (capacity) of flow permitted on the edge.
    cost (int): The objective weight or routing cost per unit of flow.
    index (int): Parallel-arc index (0-based, per (tail, head) pair).
"""

NetworkInstance.__doc__ = """
A parsed single-commodity network instance loaded from a DIMACS .min file.

Attributes:
    num_nodes (int): Total number of nodes in the network.
    num_arcs (int): Total number of directed edges in the network.
    nodes (List[int]): A list of all node IDs.
    edges (List[Edge]): A list of Edge objects containing the full topology and parameters.
    supplies (Dict[int, int]): A mapping of node IDs to their supply (positive) or demand (negative) values.
    arcs (List[Tuple[int, int]]): A list of (tail, head) tuples representing the network topology.
    capacities (List[int]): An ordered list of total capacities corresponding to the arcs list.
    weights (List[int]): An ordered list of routing costs corresponding to the arcs list.
    parallel (bool): True iff at least one ``(tail, head)`` pair has ≥ 2 arcs.
    num_parallel_arc_pairs (int): Count of distinct ``(tail, head)`` pairs with ≥ 2 arcs.
    arc_indices (Dict[Tuple[int, int], List[int]]): ``(tail, head)`` → positions in ``edges``.

Methods:
    topology() -> List[Tuple[int, int]]: ``(tail, head)`` view for ``get_adjacency_mapping``.
"""

MultiCommoditySupplies.__doc__ = """
Contains the partitioned supply/demand data across multiple commodities.

Attributes:
    partition (Dict[int, List[int]]): A mapping of node IDs to a list of supply/demand values, indexed by commodity.
"""

MultiCommodityData.__doc__ = """
The generated multicommodity data structure, lifting the base network into K-commodity space.

Attributes:
    supply_partition (Dict[int, List[int]]): Nodal supply/demand mapped to a list of values for each commodity K.
    is_uniform (bool): Flag indicating if uniform partitioning was used (True) or spread partitioning (False).
    commodity_edges (List[Tuple[int, int, int, int]]):
        ``(commodity, tail, head, index)`` triples across all commodity-arc pairs.
    capacities (List[int]): The shared, mutual capacities for each edge.
    weight (List[List[int]]): A matrix of routing costs.
    weights_by_arc (Dict[int, List[int]]): A mapping of edge indices to a list of commodity-specific costs.
    capacities_by_arc (Dict[int, List[int]]): A mapping of edge indices to a list of commodity-specific capacities.
    commodity_capacities (Dict[Tuple[int, int, int], List[int]]):
        ``(tail, head, index)`` → per-commodity capacities.
    commodity_weights (Dict[Tuple[int, int, int], List[int]]):
        ``(tail, head, index)`` → per-commodity costs.
    num_commodities (int): The total number of commodities generated (K).
    randomized_capacities (bool): Flag indicating if commodity-specific capacities were perturbed with uniform noise.
    randomized_weights (bool): Flag indicating if commodity-specific routing costs were perturbed with uniform noise.
    cap_zero (bool): Zero-capacity exclusions applied.
    cap_zero_param (float): Fraction of arcs excluded per commodity.
    seed (int): The random seed used for generating stochastic perturbations.
    parallel (bool): True iff the underlying instance has parallel arcs.
    arc_indices (Dict[Tuple[int, int], List[int]]): ``(tail, head)`` → arc positions.
"""

ParsedMulticommodityInstance.__doc__ = """
An object containing multi-commodity data parsed directly from a serialized ``.mcfmin`` file.

Attributes:
    num_nodes (int): Total number of nodes.
    num_arcs (int): Total number of directed edges in the network.
    num_commodities (int): Total number of commodities (K).
    randomized_capacities (bool): Flag indicating the presence of commodity-specific capacities.
    randomized_weights (bool): Flag indicating the presence of commodity-specific routing costs.
    nodes (List[int]): List of all node IDs.
    edges (List[Tuple[int, int, int]]): List of baseline (tail, head, index) edges.
    supplies (Dict[int, int]): Node IDs mapped to their total supply/demand.
    commodity_supply_demand_data (Dict[int, List[int]]): Node IDs mapped to their respective supply/demand arrays across commodities.
    capacities (List[int]): Shared mutual capacities of the dges.
    commodity_capacities (Dict[Tuple[int, int, int], List[int]]):
        ``(tail, head, index)`` → per-commodity capacities.
    commodity_weights (Dict[Tuple[int, int, int], List[int]]):
        ``(tail, head, index)`` → per-commodity costs.
    commodity_edges (List[Tuple[int, int, int, int]]):
        ``(commodity, tail, head, index)`` triples.
    commodity_bundle_capacities (List[int]): Flattened commodity-major capacities,
        laid out as ``bundle[k * num_arcs + position]``.
    start_nodes (List[int]): List of source nodes containing positive supply.
    end_nodes (List[int]): List of sink nodes containing negative supply (demand).
    method (int): Partitioning method.
    cap_zero (bool): Zero-capacity exclusions present.
    cap_zero_param (float): Fraction of arcs excluded per commodity.
    seed (int): The random seed used during generation.
    parallel (bool): True iff the instance has parallel arcs.
    arc_indices (Dict[Tuple[int, int], List[int]]): ``(tail, head)`` → arc positions.

Methods:
    topology() -> List[Tuple[int, int]]: ``(tail, head)`` view for ``get_adjacency_mapping``.
"""

__all__ = [
    "load_min_instance",
    "split_supplies_uniform",
    "split_supplies_spread",
    "split_supplies_beta_binomial",
    "compute_commodity_demand_heterogeneity",
    "generate_multi_commodity_data",
    "save_multi_commodity_instance",
    "load_multi_commodity_instance",
    "get_adjacency_mapping",
    "Edge",
    "NetworkInstance",
    "MultiCommoditySupplies",
    "MultiCommodityData",
    "ParsedMulticommodityInstance"
]

from .s2mflow import __doc__