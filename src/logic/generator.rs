use core::panic;
use std::collections::BTreeMap;
use std::println;
use rand::prelude::*;
use rand::{SeedableRng};
use rand::rngs::StdRng;
use rand_distr::num_traits::abs;
use rand_distr::num_traits::ops::inv;
use rand_distr::{Beta, Binomial, Distribution};

use crate::models::MultiCommodityData;


/// Sample a single value from a Beta-Binomial(n, alpha, beta) distribution.
/// 
/// The distribution is generated hierarchically:
///     1. Draw p ~ Beta(alpha, beta)
///     2. Draw X ~ Binomial(n, p)
fn sample_beta_binomial(
    rng: &mut StdRng,
    n: i64,
    alpha: f64,
    beta: f64,
) -> i64 {
    if n == 0 {
        return 0;
    }

    let beta_dist = Beta::new(alpha, beta).unwrap();
    let p: f64 = beta_dist.sample(rng);
    
    let binom_dist = Binomial::new(n as u64, p).unwrap();
    binom_dist.sample(rng) as i64
}


pub fn split_supply_and_demand_uniform(
    data: &BTreeMap<i64, i64>,
    num_commodities: usize,
) -> BTreeMap<i64, Vec<i64>> {
    let mut commodity_data: BTreeMap<i64, Vec<i64>> = BTreeMap::new();

    // next_k determines which commodity gets the 'remainder' unit.
    let mut next_k = 0;

    // BTreeMap iteration is inherently sorty by Node ID (key).
    // Truncation to zero: - 8 / 3 = -2 and -8 % 3 = -2.
    for (&node, &total_val) in data {
        // sign(b_i) floor (abs(b_i) / K)
        let base_val = total_val / (num_commodities as i64);
        let mut node_data = vec![base_val; num_commodities];

        let sign = total_val.signum();
        // abs(b_i) mod K
        let remainder = (total_val % (num_commodities as i64)).abs();

        for _ in 0..remainder {
            node_data[next_k] += sign;
            next_k = (next_k + 1) % num_commodities;
        }
        
        commodity_data.insert(node, node_data);
    }

    balance_commodities(&mut commodity_data, data, num_commodities, None);

    commodity_data
}


pub fn split_supply_and_demand_spread(
    data: &BTreeMap<i64, i64>,
    num_commodities: usize,
    seed: u64,
) -> BTreeMap<i64, Vec<i64>> {
    let mut rng = StdRng::seed_from_u64(seed);
    let mut commodity_data: BTreeMap<i64, Vec<i64>> = BTreeMap::new();

    for (&node, &demand) in data {
        if demand == 0 { continue; }

        let abs_demand = demand.abs();
        let mut sample = vec![0i64; num_commodities];
        
        let mut cuts: Vec<i64> = (0..num_commodities - 1).map(|_| rng.random_range(0..=abs_demand)).collect();
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

    balance_commodities(&mut commodity_data, data, num_commodities, Some(&mut rng));

    commodity_data
}


pub fn split_supply_and_demand_beta_binomial(
    data: &BTreeMap<i64, i64>,
    num_commodities: usize,
    concentration_param: f64,
    seed: u64,
) -> BTreeMap<i64, Vec<i64>> {
    let mut rng = StdRng::seed_from_u64(seed);
    let mut commodity_data: BTreeMap<i64, Vec<i64>> = BTreeMap::new();

    for (&node, &demand) in data {
        if demand == 0 { continue; }

        let abs_demand = demand.abs();
        let mut remaining = abs_demand;
        let mut sample = vec![0i64; num_commodities];

        for j in 0..(num_commodities - 1) {
            let x = sample_beta_binomial(
                &mut rng,
                remaining,
                concentration_param,
                concentration_param * (num_commodities - j - 1) as f64,
            );
            
            sample[j] = x;
            remaining -= x;
        }

        sample[num_commodities - 1] = remaining;

        if demand < 0 {
            for val in sample.iter_mut() {
                *val = -(*val);
            }
        }

        commodity_data.insert(node, sample);
    }

    balance_commodities(&mut commodity_data, data, num_commodities, Some(&mut rng));

    commodity_data
}


pub fn compute_commodity_demand_heterogeneity(
    partition: &BTreeMap<i64, Vec<i64>>,
    original: &BTreeMap<i64, i64>,
) -> f64 {
    if partition.is_empty() || original.is_empty() {
        return 0.0;
    }

    // Determine number of commodities from the first non-zero entry
    let mut k = 1usize;
    for vals in partition.values() {
        if !vals.is_empty() {
            k = vals.len();
            break;
        }
    }

    if k == 1 {
        return 0.0
    }

    let mut active_nodes = 0usize;
    let mut total_heterogeneity = 0.0;

    for (&node, &total_demand) in original {

        if total_demand == 0 {
            continue;
        }

        let node_partition = match partition.get(&node) {
            Some(vals) => vals,
            None => continue,
        };

        let abs_demand = (total_demand.abs()) as f64;
        let inv_k = 1.0 / (k as f64);
        let mut node_deviation = 0.0;

        for  &val in node_partition {
            let p = (val.abs() as f64) / abs_demand;
            node_deviation += (p - inv_k).abs();
        }

        // Normalize total variation distance to [0,1]
        let node_heterogeneity = (k as f64) / (2.0 * ((k - 1) as f64)) * node_deviation;

        total_heterogeneity += node_heterogeneity;
        active_nodes += 1;
    }

    if active_nodes == 0 {
        0.0
    } else {
        total_heterogeneity / (active_nodes as f64)
    }
}


fn balance_commodities(
    commodity_data: &mut BTreeMap<i64, Vec<i64>>,
    original_data: &BTreeMap<i64, i64>,
    num_commodities: usize,
    mut rng: Option<&mut StdRng>,
) {
    // 1. Compute current global balances
    let mut current_balances = vec![0i64; num_commodities];
    for sample in commodity_data.values() {
        for k in 0..num_commodities {
            current_balances[k] += sample[k];
        }
    }

    let sorted_nodes: Vec<i64> = commodity_data.keys().copied().collect();
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

        let sk = match rng.as_deref_mut() {
            Some(r) => {
                let idx = r.random_range(0..surplus_ks.len());
                surplus_ks[idx]
            }
            None => surplus_ks[0]
        };  // Pick surplus commodity randomly for spread and beta-binomial, take the first surplus commodity for uniform
       
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
    method: i64,
    randomize_caps: bool,
    cap_a: f64,
    cap_b: f64,
    randomize_costs: bool,
    cost_a: f64,
    cost_b: f64,
    concentration_param: f64,
    seed: u64,
) -> MultiCommodityData {
    let mut rng = StdRng::seed_from_u64(seed);

    let supply_partition = match method {
        0 => split_supply_and_demand_spread(&instance.supplies, num_commodities, seed),
        1 => split_supply_and_demand_uniform(&instance.supplies, num_commodities),
        2 => split_supply_and_demand_beta_binomial(
            &instance.supplies, 
            num_commodities, 
            concentration_param,
            seed
        ),
        _ => panic!("Unknown partitioning method: {}", method),
    };

    let num_original_edges = instance.edges.len();

    let mut weights_by_arc = BTreeMap::new();
    let mut capacities_by_arc = BTreeMap::new();
    let mut commodity_capacities = BTreeMap::new();
    let mut commodity_weights = BTreeMap::new();
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
                (raw_cost.ceil() as i64).max(floor_val)
            } else {
                edge.cost
            };
            arc_costs.push(cost);

            let cap = if randomize_caps {
                (rng.random_range(cap_low..cap_high).ceil() as i64).max(1)
            } else {
                edge.up
            };
            arc_caps.push(cap);
        }

        let arc_key = (edge.tail, edge.head);
        weights_by_arc.insert(i, arc_costs.clone());
        capacities_by_arc.insert(i, arc_caps.clone());
        commodity_weights.insert(arc_key, arc_costs);
        commodity_capacities.insert(arc_key, arc_caps);
    }



    let mut weight = Vec::with_capacity(num_commodities);
    for k in 0..num_commodities {
        let w: Vec<i64> = (0..num_original_edges).map(|i| weights_by_arc[&i][k]).collect();
        weight.push(w);
    }

    MultiCommodityData { 
        supply_partition,
        method,
        commodity_edges: commodity_edges, 
        capacities: base_capacities, 
        weight: weight, 
        weights_by_arc, 
        capacities_by_arc: capacities_by_arc, 
        commodity_capacities: commodity_capacities,
        commodity_weights: commodity_weights,
        num_commodities, 
        randomized_capacities: randomize_caps, 
        randomized_weights: randomize_costs, 
        seed: seed,
    }

}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{assert_eq, collections::BTreeMap, println};

    /// Test Phase 1: Local Partitioning (Node-wise Split)
    /// Goal: Ensure the sum of partitioned commodities at a node matches the original node supply.
    #[test]
    fn test_local_partitioning() {
        let mut supplies = BTreeMap::new();
        supplies.insert(1, 25);
        supplies.insert(2, -25);

        let num_commodities = 3;
        let seed = 42;
        
        // Test Uniform
        let res_uniform = split_supply_and_demand_uniform(&supplies, num_commodities);

        for (&node, &original_val) in &supplies {
            let partition = &res_uniform[&node];

            // Check Sum
            let partition_sum: i64 = partition.iter().sum();
            assert_eq!(partition_sum, original_val, "Uniform split sum mismatch at node {}", node);

            // Check Sign Consistency
            for &val in partition {
                if original_val > 0 {
                    assert!(val >= 0, "Node {} is supply (>0) but has negative commodity value {}", node, val);
                } else if original_val < 0 {
                    assert!(val <= 0, "Node {} is demand (<0) but has positive commodity value {}", node, val);
                }
            }
        }

        // Test Spread
        let res_spread = split_supply_and_demand_spread(&supplies, num_commodities, seed);

        for (&node, &original_val) in &supplies {
            let partition = &res_spread[&node];
            
            // Check sum
            let partition_sum: i64 = partition.iter().sum();
            assert_eq!(partition_sum, original_val, "Spread split sum mismatch at node {}", node);

            // Check Sign Consistency
            for &val in partition {
                if original_val > 0 {
                    assert!(val >= 0, "Node {} is supply (>0) but has negative commodity value {}", node, val);
                } else if original_val < 0 {
                    assert!(val <= 0, "Node {} is demand (<0) but has positive commodity value {}", node, val);
                }
            }
        }

        // Test Beta-Binomial
        let concentration_param = 3.0;
        let res_beta_binomial = split_supply_and_demand_beta_binomial(&supplies, num_commodities, concentration_param, seed);

        for (&node, &original_val) in &supplies {
            let partition = &res_beta_binomial[&node];

            // Check sum
            let partition_sum: i64 = partition.iter().sum();
            assert_eq!(partition_sum, original_val);

            // Check Sign Consistency
            for &val in partition {
                if original_val > 0 {
                    assert!(val >= 0, "Node {} is supply (>0) but has negative commodity value {}", node, val);
                } else if original_val < 0 {
                    assert!(val <= 0, "Node {} is demand (<0) but has positive commodity value {}", node, val);
                }
            }
        }
    }

    /// Test Phase 2: Global Balancing (Commodity-wise Zero Sum)
    /// Goal: Ensure that after balancing, the sum of a specific commodity across all nodes is 0.
    #[test]
    fn test_balance_commodities() {
        let mut commodity_data = BTreeMap::new();
        commodity_data.insert(1, vec![3, 8, 2]);
        commodity_data.insert(2, vec![0, 1, 1]);
        commodity_data.insert(3, vec![2, 0, 3]);
        commodity_data.insert(4, vec![-1, -4, -1]);
        commodity_data.insert(5, vec![-2, -9, -3]);

        let original_data = BTreeMap::from([(1, 13), (2, 2), (3, 5), (4, -6), (5, -14)]);
        let num_commodities = 3;

        balance_commodities(&mut commodity_data, &original_data, num_commodities, None);

        // Verify Global Balance: sum_i(b_i^k) == 0
        for k in 0..num_commodities {
            let global_sum: i64 = commodity_data.values().map(|v| v[k]).sum();
            assert_eq!(global_sum, 0, "Global balance failed for commodity {}", k);
        }

        // Re-verify Local  Balance (sum_k(b_i^k) == b_i) and Sign Consistency
        for (&node, &original_val) in &original_data {
            let partition = &commodity_data[&node];

            // Local Sum
            let local_sum: i64 = partition.iter().sum();
            assert_eq!(local_sum, original_val, "Local balance failed at node {} after global balancing", node);

            // Sign Consistency (Post-Balancing)
            for &val in partition {
                if original_val > 0 {
                    assert!(val >= 0, "Balancing pushed node {} (supply) to negative value {}", node, val);
                } else if original_val < 0 {
                    assert!(val <= 0, "Balanving pushed node {} (demand) to positive value {}", node, val);
                }
            }
        }

    }

    /// Test: Commodity-demand heterogeneity.
    #[test]
    fn test_heterogeneity_bounds() {
        let mut original = BTreeMap::new();
        original.insert(1, 9);
        original.insert(2, -9);

        // Uniform partition for K = 3: [3,3,3] and [-3,-3,-3]
        let mut uniform_partition = BTreeMap::new();
        uniform_partition.insert(1, vec![3, 3, 3]);
        uniform_partition.insert(2, vec![-3, -3, -3]);

        let h_uniform = compute_commodity_demand_heterogeneity(&uniform_partition, &original);
        assert!(h_uniform <= 0.000001 && h_uniform >= -0.000001);

        // Spread-like extreme partition for K = 3: [9,0,0] and [-9,0,0]
        let mut spread_partition = BTreeMap::new();
        spread_partition.insert(1, vec![9,0,0]);
        spread_partition.insert(2, vec![-9,0,0]);

        let h_spread = compute_commodity_demand_heterogeneity(&spread_partition, &original);
        assert!(h_spread <= 1.000001 && h_spread >= 0.999999)
    }

}