from typing import Dict, List, Tuple

class Edge:
    tail: int
    head: int
    low: int
    up: int
    cost: int

class NetworkInstance:
    num_nodes: int
    num_arcs: int
    nodes: List[int]
    edges: List[Edge]
    supplies: Dict[int, int]
    arcs: List[Tuple[int, int]]
    capacities: List[int]
    weights: List[int]

class MultiCommoditySupplies:
    partition: Dict[int, List[int]]

class MultiCommodityData:
    supply_partition: Dict[int, List[int]]
    is_uniform: bool
    edges: List[Tuple[int, int, int]]
    capacities: List[int]
    weight: List[List[int]]
    weights_by_arc: Dict[int, List[int]]
    capacites_by_arc: Dict[int, List[int]]
    num_commodities: int
    randomized_capacities: bool
    randomized_weights: bool
    seed: int

class ParsedMulticommodityInstance:
    num_nodes: int
    num_arcs: int
    num_commodities: int
    randomized_capacities: bool
    randomized_weights: bool
    nodes: List[int]
    edges: List[Tuple[int, int]]
    commodity_supply_demand_data: Dict[int, List[int]]
    capacities: List[int]
    commodity_capacities: Dict[Tuple[int, int], List[int]]
    commodity_weights: Dict[tuple[int, int], List[int]]
    commodity_edges: List[Tuple[int, int, int]]
    commodity_bundle_capacities: List[int]
    start_nodes: List[int]
    end_nodes: List[int]
    is_uniform: bool
    seed: int

def load_min_instance(path: str) -> NetworkInstance:
    """Loads a single-commodity network instance from a DIMACS .min file.
    
    Args:
        path (str): The filesystem path to the .min file.
        
    Returns:
        NetworkInstance: An object containing information on the min-cost flow instance.
        
    Raises:
        IOError: If the file cannot be read or the format is invalid.
    """
    ...

def split_supplies_uniform(data: Dict[int, int], num_k: int) -> Dict[int, List[int]]:
    """Partitions nodal supply/demand into K commodities using a uniform distribution.
    
    Args:
        data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
        num_k (int): The number of commodities.
        
    Returns:
        Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
    """
    ...

def split_supplies_spread(data: Dict[int, int], num_k: int, seed: int) -> Dict[int, List[int]]:
    """Partitions nodal supply/demand into K commodities using a spread distribution.
    
    Args:
        data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
        num_k (int): The number of commodities.
        seed (int): Seed.
        
    Returns:
        Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
    """
    ...

def generate_multi_commodity_data(
    instance: NetworkInstance,
    num_commodities: int,
    is_uniform: bool,
    randomize_caps: bool = False,
    cap_a: float = 0.8,
    cap_b: float = 1.2,
    randomize_costs: bool = False,
    cost_a: float = 0.8,
    cost_b: float = 1.2,
    seed: int = 42,
) -> MultiCommodityData:
    """Generates a full multi-commodity dataset from a single-commodity instance.
    
    This function handles the partitioning of supplies and the optional randomization of
    arc capacities and costs across commodities.
    
    Args:
        instance (NetworkInstance): The base single-commodity network.
        num_commodities (int): The number of commodities.
        is_uniform (bool): If True, uses uniform partitioning; otherwise, uses spread.
        randomize_caps (bool, optional): If True, varies capacities per commodity. Defaults to False.
        cap_a (float, optional): Lower multiplier for capacity randomization. Defaults to 0.8.
        cap_b (float, optional): Upper multiplier for capacity randomization. Defaults to 1.2.
        randomize_costs (bool, optional): If True, varies costs per commodity. Defaults to False.
        cost_a (float, optional): Lower multiplier for cost randomization. Defaults to 0.8.
        cost_b (float, optional): Upper multiplier for cost randomization. Defaults to 1.2.
        seed (int, optional): Seed. Defaults to 42.

    Returns:
        MultiCommodityData: The generated multi-commodity data.
    """
    ...

def save_multi_commodity_instance(
    path: str,
    instance: NetworkInstance,
    multi_data: MultiCommodityData,
) -> None:
    """Exports a multi-commodity instance to a DIMACS-formatted file.
    
    Uses a specialized hybrid format that compresses non-randomized arc data while allowing
    expanded per-commodity values when necessary.
    
    Args:
        path (str): Export destination path.
        instance (NetworkInstance): The base network topology.
        multi_data (MultiCommodityData): The multi-commodity data.
    """
    ...

def load_multi_commodity_instance(path: str) -> ParsedMulticommodityInstance:
    """Loads and parses a multi-commodity DIMACS file into a multicommodity-instance.
    
    This function reads the specialized DIMACS format generated by this package.
    
    Args:
        path (str): The filesystem path to the multi-commodity .min file.
        
    Returns:
        ParsedMulticommodityInstance: An object containing multi-commodity data.
        
    Raises:
        RuntimeError: If the file header is inconsistent or the arc data is malformed.
        IOError: If the file cannot be accessed.
    """
    ...

def get_incidence_mapping(
    nodes: list[int], 
    edges: list[tuple[int, int]]
) -> tuple[dict[int, list[int]], dict[int, list[int]]]: 
    """
    Create incidence mapping (incoming, outgoing).

    Args:
        nodes (int): List of node IDs.
        edges (List[int, int]): List of edges.
    """
    ...