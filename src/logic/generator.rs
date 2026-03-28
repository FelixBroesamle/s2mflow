use std::collections::BTreeMap;
use rand::prelude::*;
use rand::{SeedableRng};
use rand::rngs::StdRng;

use crate::models::MultiCommodityData;

pub fn split_supply_and_demand_uniform(
    data: &BTreeMap<i32, i32>,
    num_commodities: usize,
) -> BTreeMap<i32, Vec<i32>> {
    let mut commodity_data: BTreeMap<i32, Vec<i32>> = BTreeMap::new();

    // next_k determines which commodity gets the 'remainder' unit.
    let mut next_k = 0;

    // BTreeMap iteration is inherently sorty by Node ID (key).
    // Truncation to zero: - 8 / 3 = -2 and -8 % 3 = -2.
    for (&node, &total_val) in data {
        // sign(b_i) floor (abs(b_i) / K)
        let base_val = total_val / (num_commodities as i32);
        let mut node_data = vec![base_val; num_commodities];

        let sign = total_val.signum();
        // abs(b_i) mod K
        let remainder = (total_val % (num_commodities as i32)).abs();

        for _ in 0..remainder {
            node_data[next_k] += sign;
            next_k = (next_k + 1) % num_commodities;
        }
        
        commodity_data.insert(node, node_data);
    }

    balance_commodities(&mut commodity_data, data, num_commodities);

    commodity_data
}


pub fn split_supply_and_demand_spread(
    data: &BTreeMap<i32, i32>,
    num_commodities: usize,
    seed: u64,
) -> BTreeMap<i32, Vec<i32>> {
    let mut rng = StdRng::seed_from_u64(seed);
    let mut commodity_data: BTreeMap<i32, Vec<i32>> = BTreeMap::new();

    for (&node, &demand) in data {
        if demand == 0 { continue; }

        let abs_demand = demand.abs();
        let mut sample = vec![0i32; num_commodities];
        
        let mut cuts: Vec<i32> = (0..num_commodities - 1).map(|_| rng.random_range(0..=abs_demand)).collect();
        cuts.sort_unstable();

        let mut last = 0;
        for (i, cut) in cuts.into_iter().enumerate() {
            sample[i] = cut - last;
            last = cut;
        }
        sample[num_commodities - 1] = abs_demand - last;

        if demand < 0 {
            for val in sample.iter_mut() { *val = -(*val); }
        }

        commodity_data.insert(node, sample);

    }

    balance_commodities(&mut commodity_data, data, num_commodities);

    commodity_data
}


fn balance_commodities(
    commodity_data: &mut BTreeMap<i32, Vec<i32>>,
    original_data: &BTreeMap<i32, i32>,
    num_commodities: usize
) {
    // 1. Compute current global balances
    let mut current_balances = vec![0i32; num_commodities];
    for sample in commodity_data.values() {
        for k in 0..num_commodities {
            current_balances[k] += sample[k];
        }
    }

    let sorted_nodes: Vec<i32> = commodity_data.keys().copied().collect();
    let n = sorted_nodes.len();

    let mut node_ptr = 0;
    let mut deficit_ptr = 0;

    let mut surplus_ks = Vec::with_capacity(num_commodities);
    let mut deficit_ks = Vec::with_capacity(num_commodities);

    loop {
        surplus_ks.clear();
        deficit_ks.clear();

        for (k, &bal) in current_balances.iter().enumerate() {
            if bal > 0 { surplus_ks.push(k); }
            else if bal < 0 { deficit_ks.push(k); }
        }

        if surplus_ks.is_empty() || deficit_ks.is_empty() { break; }

        let sk = surplus_ks[0];  // Take the first surplus commodity to balance
       
        if deficit_ptr >= deficit_ks.len() {
            deficit_ptr = 0;
        }
        
        // Round-robin search through nodes starting from the last modified node
        for _ in 0..n {
            let node_id = sorted_nodes[node_ptr];
            let total_node_val = original_data[&node_id];
            let sample = commodity_data.get_mut(&node_id).unwrap();

            // Try to find a deficit commodity to swap with, starting from deficit_ptr
            for _ in 0..deficit_ks.len() {
                let dk = deficit_ks[deficit_ptr];

                // Logic:
                // Supply node: must have "sk" to give away.
                // Demand node: must have "dk" to receive.
                let can_swap = (total_node_val > 0 && sample[sk] > 0) || (total_node_val < 0 && sample[dk] < 0);
                
                deficit_ptr = (deficit_ptr + 1) % deficit_ks.len();

                if can_swap {
                    sample[sk] -= 1;
                    sample[dk] += 1;
                    current_balances[sk] -= 1;
                    current_balances[dk] += 1;

                    break;
                }
            }

            // Always increment node_ptr to ensure the next surplus check starts at a new node
            node_ptr = (node_ptr + 1) % n;

            if current_balances[sk] == 0 { break; }
        }
        
    }
}


pub fn generate_multi_commodity_data(
    instance: &crate::models::NetworkInstance,
    num_commodities: usize,
    is_uniform: bool,
    randomize_caps: bool,
    cap_a: f64,
    cap_b: f64,
    randomize_costs: bool,
    cost_a: f64,
    cost_b: f64,
    seed: u64,
) -> MultiCommodityData {
    let supply_partition = if is_uniform {
        split_supply_and_demand_uniform(&instance.supplies, num_commodities)
    } else {
        split_supply_and_demand_spread(&instance.supplies, num_commodities, seed)
    };

    let mut rng = StdRng::seed_from_u64(seed);
    let num_original_edges = instance.edges.len();

    let mut weights_by_arc = BTreeMap::new();
    let mut capacities_by_arc = BTreeMap::new();
    let mut commodity_edges = Vec::with_capacity(num_commodities * num_original_edges);
    let mut base_capacities = Vec::with_capacity(num_commodities * num_original_edges);

    for (i, edge) in instance.edges.iter().enumerate() {
        let c_f64 = edge.cost as f64;
        let cap_f64 = edge.up as f64;

        let cost_low = cost_a * c_f64;
        let cost_high = cost_b * c_f64;
        let cap_low = cap_a * cap_f64;
        let cap_high = cap_b * cap_f64;

        let mut arc_costs = Vec::with_capacity(num_commodities);
        let mut arc_caps = Vec::with_capacity(num_commodities);

        for k in 0..num_commodities {
            commodity_edges.push((k, edge.tail, edge.head));
            base_capacities.push(edge.up);

            let cost = if randomize_costs {
                let raw_cost = rng.random_range(cost_low..cost_high);
                let floor_val = if edge.cost == 0 { 0 } else { 1 };
                (raw_cost.ceil() as i32).max(floor_val)
            } else {
                edge.cost
            };
            arc_costs.push(cost);

            let cap = if randomize_caps {
                (rng.random_range(cap_low..cap_high).ceil() as i32).max(1)
            } else {
                edge.up
            };
            arc_caps.push(cap);
        }
        weights_by_arc.insert(i, arc_costs);
        capacities_by_arc.insert(i, arc_caps);
    }

    let mut commodity_weights = Vec::with_capacity(num_commodities);
    for k in 0..num_commodities {
        let w: Vec<i32> = (0..num_original_edges).map(|i| weights_by_arc[&i][k]).collect();
        commodity_weights.push(w);
    }

    MultiCommodityData { 
        supply_partition,
        is_uniform: is_uniform, 
        edges: commodity_edges, 
        capacities: base_capacities, 
        weight: commodity_weights, 
        weights_by_arc, 
        capacites_by_arc: capacities_by_arc, 
        num_commodities, 
        randomized_capacities: randomize_caps, 
        randomized_weights: randomize_costs, 
        seed: seed,
    }

}