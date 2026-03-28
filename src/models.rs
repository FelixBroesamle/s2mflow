use serde::{Deserialize, Serialize};
use pyo3::prelude::*;
use std::collections::{BTreeMap};

#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct Edge {
    #[pyo3(get)] pub tail: i32,
    #[pyo3(get)] pub head: i32,
    #[pyo3(get)] pub low: i32,
    #[pyo3(get)] pub up: i32,
    #[pyo3(get)] pub cost: i32,
}

#[pyclass]
#[derive(Clone, Serialize, Deserialize, Debug)]
pub struct NetworkInstance {
    #[pyo3(get)] pub num_nodes: i32,
    #[pyo3(get)] pub num_arcs: i32,
    #[pyo3(get)] pub nodes: Vec<i32>,
    #[pyo3(get)] pub edges: Vec<Edge>,
    #[pyo3(get)] pub supplies: BTreeMap<i32, i32>,
    #[pyo3(get)] pub arcs: Vec<(i32, i32)>,
    #[pyo3(get)] pub capacities: Vec<i32>,
    #[pyo3(get)] pub weights: Vec<i32>,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct MultiCommoditySupplies {
    #[pyo3(get)]
    pub partition: BTreeMap<i32, Vec<i32>>,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct MultiCommodityData {
    #[pyo3(get)] pub supply_partition: BTreeMap<i32, Vec<i32>>,
    #[pyo3(get)] pub is_uniform: bool,
    #[pyo3(get)] pub edges: Vec<(usize, i32, i32)>,
    #[pyo3(get)] pub capacities: Vec<i32>,
    #[pyo3(get)] pub weight: Vec<Vec<i32>>,
    #[pyo3(get)] pub weights_by_arc: BTreeMap<usize, Vec<i32>>,
    #[pyo3(get)] pub capacites_by_arc: BTreeMap<usize, Vec<i32>>,
    #[pyo3(get)] pub num_commodities: usize,
    #[pyo3(get)] pub randomized_capacities: bool,
    #[pyo3(get)] pub randomized_weights: bool,
    #[pyo3(get)] pub seed: u64,
}

#[pyclass]
#[derive(Clone, Debug)]
pub struct ParsedMulticommodityInstance {
    #[pyo3(get)] pub num_nodes: i32,
    #[pyo3(get)] pub num_arcs: i32,
    #[pyo3(get)] pub num_commodities: usize,
    #[pyo3(get)] pub randomized_capacities: bool,
    #[pyo3(get)] pub randomized_weights: bool,
    #[pyo3(get)] pub nodes: Vec<i32>,
    #[pyo3(get)] pub edges: Vec<(i32, i32)>,
    #[pyo3(get)] pub commodity_supply_demand_data: BTreeMap<i32, Vec<i64>>,
    #[pyo3(get)] pub capacities: Vec<i32>,
    #[pyo3(get)] pub commodity_capacities: BTreeMap<(i32, i32), Vec<i64>>,
    #[pyo3(get)] pub commodity_weights: BTreeMap<(i32, i32), Vec<i64>>,
    #[pyo3(get)] pub commodity_edges: Vec<(usize, i32, i32)>,
    #[pyo3(get)] pub commodity_bundle_capacities: Vec<i32>,
    #[pyo3(get)] pub start_nodes: Vec<i32>,
    #[pyo3(get)] pub end_nodes: Vec<i32>,
    #[pyo3(get)] pub is_uniform: bool,
    #[pyo3(get)] pub seed: u64,
}
