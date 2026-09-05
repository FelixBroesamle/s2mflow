//! s2mflow: A high-performance bridge for transforming single-commodity network flow
//! instances into multi-commodity flow instances.

mod models;
mod utils;
mod logic;

use pyo3::prelude::*;
use std::collections::BTreeMap;

use crate::models::{MultiCommodityData, NetworkInstance};

///Loads a single-commodity network instance from a DIMACS .min file.
/// 
/// Args:
///     path (str): The filesystem path to the .min file.
/// 
/// Returns:
///     NetworkInstance: An object containing information on the min-cost flow instance.
/// 
/// Raises:
///     IOError: If the file cannot be read or the format is invalid.
#[pyfunction]
pub fn load_min_instance(
    path: String
) -> PyResult<models::NetworkInstance> {
    utils::parse_min(&path).map_err(|e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string()))
}

/// Partitions nodal supply/demand into K commodities using a uniform distribution.
/// 
/// Args:
///     data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
///     num_commodities (int): The number of commodities.
/// 
/// Returns:
///     Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands
#[pyfunction]
#[pyo3(signature = (data, num_commodities))]
pub fn split_supplies_uniform(
    data: BTreeMap<i64, i64>, 
    num_commodities: usize
) -> BTreeMap<i64, Vec<i64>> {
    logic::generator::split_supply_and_demand_uniform(
        &data, 
        num_commodities,
    )
}

/// Partitions nodal supply/demand into K commodities using a spread distribution.
/// 
/// Args:
///     data (Dict[int, int]): A mapping of node IDs to their total supply/demand.
///     num_commodities (int): The number of commodities.
///     seed (int): Seed.
/// 
/// Returns:
///     Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies/demands.
#[pyfunction]
#[pyo3(signature = (data, num_commodities, seed))]
pub fn split_supplies_spread(
    data: BTreeMap<i64, i64>,
    num_commodities: usize,
    seed: u64,
) -> BTreeMap<i64, Vec<i64>> {
    logic::generator::split_supply_and_demand_spread(
        &data, 
        num_commodities,
        seed,
    )
}

/// Partitions nodal supply/demand into K commodities using a beta-binomial distribution.
/// 
/// Args:
///     data (Dict[int, int]): A mapping of node IDs to the total supply/demand.
///     num_commodities (int): The number of commodities.
///     concentration_param (float): Concentration parameter for Beta-Binomial distribution. Defaults to 3.0.
///     seed (int): Seed.
/// 
/// Returns:
///     Dict[int, List[int]]: A mapping where each node ID points to a list of the commodity supplies / demands.
#[pyfunction]
#[pyo3(signature = (
    data, 
    num_commodities, 
    concentration_param=3.0, 
    seed=42,
))]
pub fn split_supplies_beta_binomial(
    data: BTreeMap<i64, i64>,
    num_commodities: usize,
    concentration_param: f64,
    seed: u64,
) -> BTreeMap<i64, Vec<i64>> {
    logic::generator::split_supply_and_demand_beta_binomial(
        &data, 
        num_commodities, 
        concentration_param,
        seed
    )
}

/// Computes the commodity-demand heterogeneity H(B) of a given partition.
/// 
/// The metric is defined as the average total variation distance between the commodity-share vector of each active node and the uniform distribution.
/// Its value lies in [0, 1].
/// 
/// Args: 
///     partition (Dict[int, List[int]]): Mapping from node ID to commodity demands.
///     original (Dict[int, int]): Original single-commodity demands.
///
/// Returns:
///     float: Commodity-demand heterogeneity in [0,1].
#[pyfunction]
#[pyo3(signature = (partition, original))]
pub fn compute_commodity_demand_heterogeneity(
    partition: BTreeMap<i64, Vec<i64>>,
    original: BTreeMap<i64, i64>,
) -> f64 {
    logic::generator::compute_commodity_demand_heterogeneity(
        &partition, 
        &original,
    )
}

/// Generates a full multi-commodity dataset from a single-commodity instance.
/// 
/// This function handles the partitioning of supplies and the optional randomization of
/// arc capacities and costs across commodities.
/// 
/// Args:
///     instance (NetworkInstance): The base single-commodity network.
///     num_commodities (int): The number of commodities.
///     method (int): Partitioning method. 0 = Spread, 1 = Uniform, 2 = Beta-Binomial.
///     randomize_caps (bool, optional): If True, varies capacities per commodity. Default to False.
///     cap_a (float, optional): Lower multiplier for capacity randomization. Defaults to 0.8.
///     cap_b (float, optional): Upper multiplier for capacity randomization. Defaults to 1.0.
///     randomize_costs (bool, optional): If True, varies costs per commodity. Defaults to False.
///     cost_a (float, optional): Lower multiplier for cost randomization. Defaults to 0.8.
///     cost_b (float, optional): Upper multiplier for cost randomization. Defaults to 1.2.
///     concentation_param (float, optional): Concentration parameter for Beta-Binomial distribution. Defaults to 3.0.
///     cap_zero (bool, optional): If True, set a fraction of individual capacities to zero. Defaults to False.
///     cap_zero_param (float, optional): Fraction of arcs excluded per commmodity. Defaults to 0.0.
///     seed (int, optional): Seed.
/// 
/// If cap_zero is True and cap_zero_param > 0, at least one arc per commodity is excluded.
/// 
/// Returns:
///     MultiCommodityData: The generated multi-commodity data.
#[pyfunction]
#[pyo3(signature = (
    instance, 
    num_commodities, 
    method, 
    randomize_caps=false, 
    cap_a=0.8, 
    cap_b=1.0, 
    randomize_costs=false, 
    cost_a=0.8, 
    cost_b=1.2,
    concentration_param=3.0,
    cap_zero=false,
    cap_zero_param=0.0,
    seed=42,
))]
pub fn generate_multi_commodity_data(
    instance: &models::NetworkInstance, 
    num_commodities: usize, 
    method: i64,
    randomize_caps: bool,
    cap_a: f64,
    cap_b: f64,
    randomize_costs: bool,
    cost_a: f64,
    cost_b: f64,
    concentration_param: f64,
    cap_zero: bool,
    cap_zero_param: f64,
    seed: u64,
) -> MultiCommodityData {
    logic::generator::generate_multi_commodity_data(
        instance, 
        num_commodities, 
        method,
        randomize_caps,
        cap_a,
        cap_b,
        randomize_costs,
        cost_a,
        cost_b,
        concentration_param,
        cap_zero,
        cap_zero_param,
        seed,
    )
}

/// Exports a multi-commodity instance to a DIMACS-formatted file.
/// 
/// Uses a specialized hybrid format that compresses non-randomized arc data while allowing
/// expanded per-commodity values when necessary.
/// 
/// Args:
///     path (str): Export destination path.
///     instance (NetworkInstance): The base network topology.
///     multi_data (MultiCommodityData): The multi-commodity data.
/// 
#[pyfunction]
pub fn save_multi_commodity_instance(
    path: String,
    instance: &NetworkInstance,
    multi_data: &MultiCommodityData,
) -> PyResult<()> {
    crate::utils::export_to_dimacs(
        &path, 
        instance, 
        multi_data,
    ).map_err(
        |e| PyErr::new::<pyo3::exceptions::PyIOError, _>(e.to_string())
    )
}

/// Loads and parses a multi-commodity DIMACS file into a multicommodity-instance.
/// 
/// This function reads the specialized DIMACS format generated by this package.
/// It reconstructs the multicommodity instance.
/// 
/// Args:
///     path (str): The filesystem path to the multi-commodity .min file.
/// 
/// Returns:
///     ParsedMulticommodityInstance: An object containing multi-commodity data.
/// 
/// Raises:
///     RuntimeError: If the file header is inconsistent or the arc data is malformed.
///     IOError: If the file cannot be accessed.
#[pyfunction]
pub fn load_multi_commodity_instance(
    path: String
) -> PyResult<models::ParsedMulticommodityInstance> {
    utils::parse_multi_min(
        &path
    ).map_err(
        |e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string())
    )
}

/// Creates adjacency mapping from nodes and edges.
/// 
/// Args: 
///     nodes (List[int]): List of node IDs.
///     edges (List[int, int]): List of edges.
/// 
/// Returns:
///     Tuple[Dict[int, List[int]], Dict[int, List[int]]]: Incoming and outgoing.
#[pyfunction]
#[pyo3(signature = (nodes, edges))]
pub fn get_adjacency_mapping(
    nodes: Vec<i64>,
    edges: Vec<(i64, i64)>
) -> (BTreeMap<i64, Vec<i64>>, BTreeMap<i64, Vec<i64>>) {
    crate::utils::get_adjacency_mapping(
        nodes, 
        edges
    )
}

#[pymodule]
pub fn s2mflow(
    _py: Python, 
    m: &Bound<'_, PyModule>
) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(load_min_instance, m)?)?;
    m.add_function(wrap_pyfunction!(split_supplies_uniform, m)?)?;
    m.add_function(wrap_pyfunction!(split_supplies_spread, m)?)?;
    m.add_function(wrap_pyfunction!(split_supplies_beta_binomial, m)?)?;
    m.add_function(wrap_pyfunction!(compute_commodity_demand_heterogeneity, m)?)?;
    m.add_function(wrap_pyfunction!(generate_multi_commodity_data, m)?)?;
    m.add_function(wrap_pyfunction!(save_multi_commodity_instance, m)?)?;
    m.add_function(wrap_pyfunction!(load_multi_commodity_instance, m)?)?;
    m.add_function(wrap_pyfunction!(get_adjacency_mapping, m)?)?;
    m.add_class::<models::Edge>()?;
    m.add_class::<models::NetworkInstance>()?;
    m.add_class::<models::MultiCommoditySupplies>()?;
    m.add_class::<models::MultiCommodityData>()?;
    m.add_class::<models::ParsedMulticommodityInstance>()?;
    Ok(())
}
