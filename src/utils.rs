use std::fs::File;
use std::io::{BufRead, BufReader, Write, BufWriter};
use std::collections::{BTreeMap, BTreeSet};
use crate::models::{Edge, MultiCommodityData, NetworkInstance, ParsedMulticommodityInstance};

pub fn parse_min(path: &str) -> Result<NetworkInstance, Box<dyn std::error::Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut num_nodes = 0;
    let mut num_arcs = 0;
    let mut nodes = Vec::new();
    let mut node_seen = BTreeSet::new();
    let mut edges = Vec::new();
    let mut supplies = BTreeMap::new();
    let mut arcs = Vec::new();
    let mut capacities = Vec::new();
    let mut weights = Vec::new();

    let mut pair_counter: BTreeMap<(i64, i64), i64> = BTreeMap::new();
    let mut arc_indices: BTreeMap<(i64, i64), Vec<usize>> = BTreeMap::new();

    for line in reader.lines() {
        let l = line?;
        let trimmed = l.trim();
        
        if trimmed.is_empty() || trimmed.starts_with('c') {continue};

        let tokens: Vec<&str> = trimmed.split_whitespace().collect();
        if tokens.is_empty() { continue }

        match tokens[0] {
            "p" => {
                // p min nodes arcs
                num_nodes = tokens[2].parse()?;
                num_arcs = tokens[3].parse()?;

                edges.reserve(num_arcs as usize);
                arcs.reserve(num_arcs as usize);
                capacities.reserve(num_arcs as usize);
                weights.reserve(num_arcs as usize);
            }
            "n" => {
                let node_id: i64 = tokens[1].parse()?;
                let val: i64 = tokens[2].parse()?;
                supplies.insert(node_id, val);

                if node_seen.insert(node_id) {
                    nodes.push(node_id);
                }
            }
            "a" => {
                let tail: i64 = tokens[1].parse()?;
                let head: i64 = tokens[2].parse()?;
                let low: i64 = tokens[3].parse()?;
                let up: i64= tokens[4].parse()?;
                let cost: i64 = tokens[5].parse()?;

                let slot = pair_counter.entry((tail, head)).or_insert(-1);
                *slot += 1;
                let index = *slot;

                let position = edges.len();
                edges.push(Edge { tail, head, low, up, cost, index });

                for &node in &[tail, head] {
                    if node_seen.insert(node) {
                        nodes.push(node);
                    }
                }

                arcs.push((tail, head, index));
                capacities.push(up);
                weights.push(cost);
                arc_indices.entry((tail, head)).or_default().push(position);
            }
            _ => {}
        }
    }

    let num_parallel_arc_pairs = arc_indices.values().filter(|v| v.len() > 1).count();
    let parallel = num_parallel_arc_pairs > 0;

    Ok(NetworkInstance {
        num_nodes,
        num_arcs,
        nodes,
        edges,
        supplies,
        arcs,
        capacities,
        weights,
        parallel,
        num_parallel_arc_pairs,
        arc_indices,
    })
}


pub fn parse_multi_min(path: &str) -> Result<ParsedMulticommodityInstance, Box<dyn std::error::Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut num_nodes = 0;
    let mut num_arcs = 0;
    let mut num_commodities: usize = 0;
    let mut rand_caps = false;
    let mut rand_costs = false;
    let mut seed = 0;
    let mut method: i64 = 0;
    let mut cap_zero = false;
    let mut cap_zero_param = 0.0;
    let mut has_multi_caps = false;

    let mut nodes = Vec::new();
    let mut node_seen = BTreeSet::new();
    let mut edges = Vec::new();
    let mut supplies = BTreeMap::new();
    let mut commodity_supply_demand_data = BTreeMap::new();
    let mut capacities = Vec::new();
    let mut commodity_capacities = BTreeMap::new();
    let mut commodity_weights = BTreeMap::new();
    let mut start_nodes = Vec::new();
    let mut end_nodes = Vec::new();

    let mut arc_indices: BTreeMap<(i64, i64), Vec<usize>> = BTreeMap::new();
    let mut pair_counter: BTreeMap<(i64, i64), i64> = BTreeMap::new();

    for line in reader.lines() {
        let l = line?;
        let trimmed = l.trim();

        if trimmed.is_empty() || trimmed.starts_with("c") {
            continue;
        }

        let tokens: Vec<&str> = trimmed.split_whitespace().collect();
        let tag = tokens[0];

        match tag {
            "p" => {
                num_nodes = tokens[2].parse()?;
                num_arcs = tokens[3].parse()?;
                num_commodities = tokens[4].parse()?;
                seed = tokens[10].parse()?;

                rand_caps = tokens.get(5).map_or(Ok(0), |t| t.parse::<i64>())? != 0;
                rand_costs = tokens.get(6).map_or(Ok(0), |t| t.parse::<i64>())? != 0;
                method = tokens.get(7).map_or(Ok(0), |t| t.parse::<i64>())?;
                cap_zero = tokens.get(8).map_or(Ok(0), |t| t.parse::<i64>())? != 0;
                cap_zero_param = tokens.get(9).map_or(Ok(0.0), |t| t.parse::<f64>())?;

                has_multi_caps = rand_caps || cap_zero;

                edges.reserve(num_arcs as usize);
                capacities.reserve(num_arcs as usize);
                start_nodes.reserve(num_arcs as usize);
                end_nodes.reserve(num_arcs as usize);
            }

            "n" => {
                let node_id: i64 = tokens[1].parse::<i64>()?;
                let supply_val: i64 = tokens[2].parse::<i64>()?;
                let supply_vals: Vec<i64> = tokens[3..].iter().map(|&t| t.parse::<i64>()).collect::<Result<Vec<_>, _>>()?;

                supplies.insert(node_id, supply_val);

                commodity_supply_demand_data.insert(node_id, supply_vals);

                if node_seen.insert(node_id) {
                    nodes.push(node_id);
                }
            }

            "a" => {
                let u: i64 = tokens[1].parse::<i64>()?;
                let v: i64 = tokens[2].parse::<i64>()?;
                let up: i64 = tokens[4].parse()?;

                let k = num_commodities;
                let mut current_idx = 5;

                let parsed_caps: Vec<i64> = if has_multi_caps {
                    let res = tokens[current_idx..(current_idx + k)].iter().map(|&t| t.parse::<i64>()).collect::<Result<Vec<_>, _>>()?;
                    current_idx += k;
                    res
                } else {
                    let val = tokens[current_idx].parse::<i64>()?;
                    current_idx += 1;
                    vec![val; k]
                };

                let parsed_costs: Vec<i64> = if rand_costs {
                    let res = tokens[current_idx..(current_idx + k)].iter().map(|&t| t.parse::<i64>()).collect::<Result<Vec<_>, _>>()?;
                    res
                } else {
                    let val = tokens[current_idx].parse::<i64>()?;
                    vec![val; k]
                };

                let slot = pair_counter.entry((u, v)).or_insert(-1);
                *slot += 1;
                let index = *slot;

                let position = edges.len();

                edges.push((u, v, index));
                capacities.push(up);
                start_nodes.push(u);
                end_nodes.push(v);
                arc_indices.entry((u, v)).or_default().push(position);
                
                let key = (u, v, index);
                commodity_capacities.insert(key, parsed_caps);
                commodity_weights.insert(key, parsed_costs);

                for &node in &[u, v] {
                    if node_seen.insert(node) {
                        nodes.push(node);
                    }
                }
            }
            _ => {}
        }
    }

    let num_parallel_arc_pairs  = arc_indices.values().filter(|v| v.len() > 1).count();
    let parallel = num_parallel_arc_pairs > 0;

    let mut commodity_edges = Vec::with_capacity(num_commodities * edges.len());
    for k in 0..num_commodities {
        for &(u, v, idx) in &edges {
            commodity_edges.push((k, u, v, idx));
        }
    }

    let mut commodity_bundle_capacities = Vec::with_capacity(num_commodities * capacities.len());
    for k in 0..num_commodities {
        for &(u, v, idx) in &edges {
            commodity_bundle_capacities.push(commodity_capacities[&(u, v, idx)][k]);
        }
    }

    Ok(ParsedMulticommodityInstance { 
        num_nodes: num_nodes, 
        num_arcs: num_arcs, 
        num_commodities: num_commodities,
        randomized_capacities: rand_caps,
        randomized_weights: rand_costs, 
        nodes: nodes, 
        edges: edges, 
        supplies: supplies,
        commodity_supply_demand_data: commodity_supply_demand_data, 
        capacities: capacities, 
        commodity_capacities: commodity_capacities,
        commodity_weights: commodity_weights,
        commodity_edges: commodity_edges,
        start_nodes: start_nodes, 
        end_nodes: end_nodes, 
        method: method,
        cap_zero: cap_zero,
        cap_zero_param: cap_zero_param,
        seed: seed,
        parallel: parallel,
        arc_indices: arc_indices,
        commodity_bundle_capacities: commodity_bundle_capacities,
    })
}

pub fn export_to_dimacs(
    path: &str,
    instance: &NetworkInstance,
    multi_data: &MultiCommodityData,
) -> std::io::Result<()> {
    let file = File::create(path)?;
    let mut writer = BufWriter::new(file);

    let write_seed = if multi_data.method == 1 
        && !multi_data.randomized_capacities 
        && !multi_data.randomized_weights {
        0
    } else {
        multi_data.seed
    };
    
    // 1. Header
    writeln!(writer, "c Multicommodity flow generated by s2mflow")?;

    // 2. Problem Line: p min <nodes> <arcs> <commodities>
    let rand_caps_int = multi_data.randomized_capacities as i64;
    let rand_costs_int = multi_data.randomized_weights as i64;
    let cap_zero_int = multi_data.cap_zero  as i64;

    // p min num_nodes num_arcs num_commodities rand_caps rand_costs is_uniform seed
    writeln!(
        writer,
        "p min {} {} {} {} {} {} {} {} {}",
        instance.num_nodes,
        instance.num_arcs,
        multi_data.num_commodities,
        rand_caps_int,
        rand_costs_int,
        multi_data.method,
        cap_zero_int,
        multi_data.cap_zero_param,
        write_seed,
    )?;

    // 3. Node Lines: n <id> <total_supply> <c1> <c2> ...
    for (&node_id, supplies) in &multi_data.supply_partition {
        let total_supply: i64 = supplies.iter().sum();
        let supplies_str: Vec<String> = supplies.iter().map(|s| s.to_string()).collect();
        writeln!(writer, "n {} {} {}", node_id, total_supply, supplies_str.join(" "))?;
    }

    // 4. Arc Lines: a <tail> <head> <low> <upp> <cost_c1> <cost_c2> ...
    // Writing `instance.edges` in order guarantees that the k-th occurrence of (tail, head) gets index k-1 on round-trip.
    for (i, edge) in instance.edges.iter().enumerate() {
        let caps = &multi_data.capacities_by_arc[&i];
        let costs = &multi_data.weights_by_arc[&i];

        let write_per_commodity_caps = multi_data.randomized_capacities || multi_data.cap_zero;
        let caps_to_write = if write_per_commodity_caps {
            caps.as_slice()
        } else {
            &caps[0..1]
        };

        let costs_to_write = if multi_data.randomized_weights { costs.as_slice() } else { &costs[0..1]};

        let caps_str: Vec<String> = caps_to_write.iter().map(|c| c.to_string()).collect();
        let costs_str: Vec<String> = costs_to_write.iter().map(|c| c.to_string()).collect();

        writeln!(
            writer,
            "a {} {} {} {} {} {}",
            edge.tail, edge.head, edge.low, edge.up, caps_str.join(" "), costs_str.join(" ")
        )?;
    }

    writer.flush()?;
    Ok(())
}

pub fn get_adjacency_mapping(
    nodes: Vec<i64>,
    edges: Vec<(i64, i64)>
) -> (BTreeMap<i64, Vec<i64>>, BTreeMap<i64, Vec<i64>>) {
    let mut incoming: BTreeMap<i64, Vec<i64>> = BTreeMap::new();
    let mut outgoing: BTreeMap<i64, Vec<i64>> = BTreeMap::new();

    for &node in &nodes {
        incoming.entry(node).or_default();
        outgoing.entry(node).or_default();
    }

    for (tail, head) in edges {
        incoming.entry(head).or_default().push(tail);
        outgoing.entry(tail).or_default().push(head);
    }

    (incoming, outgoing)
}
