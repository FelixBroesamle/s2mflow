from typing import Dict, List, Tuple

class Edge:
    """Represents a single directed edge within the network."""
    tail: int
    head: int
    low: int
    up: int
    cost: int

class NetworkInstance:
    """A parsed single-commodity network instance loaded from a DIMACS .min file."""
    num_nodes: int
    num_arcs: int
    nodes: List[int]
    edges: List[Edge]
    supplies: Dict[int, int]
    arcs: List[Tuple[int, int]]
    capacities: List[int]
    weights: List[int]

class MultiCommoditySupplies:
    """Contains the partitioned supply/demand data across multiple commodities."""
    partition: Dict[int, List[int]]

class MultiCommodityData:
    """The generated multicommodity data structure, lifting the base network into K dimensions."""
    supply_partition: Dict[int, List[int]]
    method: int
    commodity_edges: List[Tuple[int, int, int]]
    capacities: List[int]
    weight: List[List[int]]
    weights_by_arc: Dict[int, List[int]]
    capacities_by_arc: Dict[int, List[int]]
    commodity_capacities: Dict[Tuple[int, int], List[int]]
    commodity_weights: Dict[Tuple[int, int], List[int]]
    num_commodities: int
    randomized_capacities: bool
    randomized_weights: bool
    seed: int

class ParsedMulticommodityInstance:
    """An object containing multi-commodity data parsed directly from a serialized .mcfmin file."""
    num_nodes: int
    num_arcs: int
    num_commodities: int
    randomized_capacities: bool
    randomized_weights: bool
    nodes: List[int]
    edges: List[Tuple[int, int]]
    supplies: Dict[int, int]
    commodity_supply_demand_data: Dict[int, List[int]]
    capacities: List[int]
    commodity_capacities: Dict[Tuple[int, int], List[int]]
    commodity_weights: Dict[tuple[int, int], List[int]]
    commodity_edges: List[Tuple[int, int, int]]
    commodity_bundle_capacities: List[int]
    start_nodes: List[int]
    end_nodes: List[int]
    method: int
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

def split_supplies_uniform(data: Dict[int, int], num_commodities: int) -> Dict[int, List[int]]:
    """Partitions nodal supply/demand into K commodities using a uniform distribution.
    
    Args:
        data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
        num_commodities (int): The number of commodities.
        
    Returns:
        Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
    """
    ...

def split_supplies_spread(data: Dict[int, int], num_commodities: int, seed: int) -> Dict[int, List[int]]:
    """Partitions nodal supply/demand into K commodities using a spread distribution.
    
    Args:
        data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
        num_commodities (int): The number of commodities.
        seed (int): Seed.
        
    Returns:
        Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
    """
    ...

def split_supplies_beta_binomial(data: Dict[int, int], num_commodities: int, concentration_param: float, seed: int) -> Dict[int, List[int]]:
    """Partitions nodal supply/demand into K commodities using a beta-binomial distribution.
    
    Args:
        data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
        num_commodities (int): The number of commodities.
        concentration_param (float): Concentration parameter for the Beta-Binomial distribution. Defaults to 3.0.
        seed (int): Seed.

    Return:
        Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
    """
    ...

def compute_commodity_demand_heterogeneity(partition: Dict[int, List[int]], original: Dict[int, int]) -> float:
    """Computes the commodity-demand heterogeneity H(B) of a given partition.

    Args: 
        partition (Dict[int, List[int]): Mapping from node ID to commodity demands.
        original (Dict[int, int]): Original single-commodity demands.
    
    Returns:
        float: Commodity-demand heterogeneity in [0,1].
    """
    ...

def generate_multi_commodity_data(
    instance: NetworkInstance,
    num_commodities: int,
    method: int,
    randomize_caps: bool = False,
    cap_a: float = 0.8,
    cap_b: float = 1.0,
    randomize_costs: bool = False,
    cost_a: float = 0.8,
    cost_b: float = 1.2,
    concentration_param: float = 3.0,
    seed: int = 42,
) -> MultiCommodityData:
    """Generates a full multi-commodity dataset from a single-commodity instance.
    
    This function handles the partitioning of supplies and the optional randomization of
    arc capacities and costs across commodities.
    
    Args:
        instance (NetworkInstance): The base single-commodity network.
        num_commodities (int): The number of commodities.
        method (int): Partitioning method. 0 = Spread, 1 = Uniform, 2 = Beta-Binomial.
        randomize_caps (bool, optional): If True, varies capacities per commodity. Defaults to False.
        cap_a (float, optional): Lower multiplier for capacity randomization. Defaults to 0.8.
        cap_b (float, optional): Upper multiplier for capacity randomization. Defaults to 1.2.
        randomize_costs (bool, optional): If True, varies costs per commodity. Defaults to False.
        cost_a (float, optional): Lower multiplier for cost randomization. Defaults to 0.8.
        cost_b (float, optional): Upper multiplier for cost randomization. Defaults to 1.2.
        concentration_param (float, optional): Concetration parameter for the Beta-Binomial distribution. Defaults to 3.0.
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

def get_adjacency_mapping(
    nodes: list[int], 
    edges: list[tuple[int, int]]
) -> tuple[dict[int, list[int]], dict[int, list[int]]]: 
    """
    Create adjacency mapping (incoming, outgoing).

    Args:
        nodes (int): List of node IDs.
        edges (List[int, int]): List of edges.
    """
    ...