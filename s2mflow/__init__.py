from .s2mflow import (
    load_min_instance,
    split_supplies_uniform,
    split_supplies_spread,
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

Attributes:
    tail (int): The source node ID of the edge.
    head (int): The destination node ID of the edge.
    low (int): The lower bound of flow permitted on the edge.
    up (int): The upper bound (capacity) of flow permitted on the edge.
    cost (int): The objective weight or routing cost per unit of flow.
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
    commodity_edges (List[Tuple[int, int, int]]): A list of (commodity_id, tail, head) tuples for commodity-wise edges.
    capacities (List[int]): The shared, mutual capacities for each edge.
    weight (List[List[int]]): A matrix of routing costs.
    weights_by_arc (Dict[int, List[int]]): A mapping of edge indices to a list of commodity-specific costs.
    capacities_by_arc (Dict[int, List[int]]): A mapping of edge indices to a list of commodity-specific capacities.
    commodity_capacities (Dict[Tuple[int, int], List[int]]): A mapping of (tail, head) tuples to a list of commodity-specific capacities.
    commodity_weights (Dict[Tuple[int, int], List[int]]): A mapping of (tail, head) tuples to a list of commodity-specific costs.
    num_commodities (int): The total number of commodities generated (K).
    randomized_capacities (bool): Flag indicating if commodity-specific capacities were perturbed with uniform noise.
    randomized_weights (bool): Flag indicating if commodity-specific routing costs were perturbed with uniform noise.
    seed (int): The random seed used for generating stochastic perturbations.
"""

ParsedMulticommodityInstance.__doc__ = """
An object containing multi-commodity data parsed directly from a serialized .mcfmin file.

Attributes:
    num_nodes (int): Total number of nodes.
    num_arcs (int): Total number of directed edges in the network.
    num_commodities (int): Total number of commodities (K).
    randomized_capacities (bool): Flag indicating the presence of commodity-specific capacities.
    randomized_weights (bool): Flag indicating the presence of commodity-specific routing costs.
    nodes (List[int]): List of all node IDs.
    edges (List[Tuple[int, int]]): List of baseline (tail, head) edges.
    supplies (Dict[int, int]): Node IDs mapped to their total supply/demand.
    commodity_supply_demand_data (Dict[int, List[int]]): Node IDs mapped to their respective supply/demand arrays across commodities.
    capacities (List[int]): Shared mutual capacities of the dges.
    commodity_capacities (Dict[Tuple[int, int], List[int]]): Commodity-specific capacities keyed by (tail, head).
    commodity_weights (Dict[Tuple[int, int], List[int]]): Commodity-specific routing costs keyed by (tail, head).
    commodity_edges (List[Tuple[int, int, int]]): A list of (commodity_id, tail, head) tuples for commodity-wise edge.
    start_nodes (List[int]): List of source nodes containing positive supply.
    end_nodes (List[int]): List of sink nodes containing negative supply (demand).
    is_uniform (bool): Flag indicating if the instance was generated using uniform partitioning.
    seed (int): The random seed used during generation.
"""

__all__ = [
    "load_min_instance",
    "split_supplies_uniform",
    "split_supplies_spread",
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