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

    for line in reader.lines() {
        let l = line?;
        if l.is_empty() || l.starts_with('c') || l.starts_with(' ') {
            continue;
        }

        let tokens: Vec<&str> = l.split_whitespace().collect();
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
                let node_id: i32 = tokens[1].parse()?;
                let val: i32 = tokens[2].parse()?;
                supplies.insert(node_id, val);

                if node_seen.insert(node_id) {
                    nodes.push(node_id);
                }
            }
            "a" => {
                let tail: i32 = tokens[1].parse()?;
                let head: i32 = tokens[2].parse()?;
                let low: i32 = tokens[3].parse()?;
                let up: i32 = tokens[4].parse()?;
                let cost: i32 = tokens[5].parse()?;

                edges.push(Edge { tail, head, low, up, cost });

                for &node in &[tail, head] {
                    if node_seen.insert(node) {
                        nodes.push(node);
                    }
                }

                arcs.push((tail, head));
                capacities.push(up);
                weights.push(cost);
            }
            _ => {}
        }
    }

    Ok(NetworkInstance {
        num_nodes,
        num_arcs,
        nodes,
        edges,
        supplies,
        arcs,
        capacities,
        weights,
    })
}


pub fn parse_multi_min(path: &str) -> Result<ParsedMulticommodityInstance, Box<dyn std::error::Error>> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut num_nodes = 0;
    let mut num_arcs = 0;
    let mut num_commodities = 0;
    let mut rand_caps = false;
    let mut rand_costs = false;
    let mut seed = 0;
    let mut is_uniform = false;

    let mut nodes = Vec::new();
    let mut node_seen = BTreeSet::new();
    let mut edges = Vec::new();
    let mut commodity_supply_demand_data = BTreeMap::new();
    let mut capacities = Vec::new();
    let mut commodity_capacities = BTreeMap::new();
    let mut commodity_weights = BTreeMap::new();
    let mut start_nodes = Vec::new();
    let mut end_nodes = Vec::new();

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
                seed = tokens[8].parse()?;

                rand_caps = tokens.get(5).map_or(Ok(0), |t| t.parse::<i32>())? != 0;
                rand_costs = tokens.get(6).map_or(Ok(0), |t| t.parse::<i32>())? != 0;
                is_uniform = tokens.get(7).map_or(Ok(0), |t| t.parse::<i32>())? != 0;

                edges.reserve(num_arcs as usize);
                capacities.reserve(num_arcs as usize);
                start_nodes.reserve(num_arcs as usize);
                end_nodes.reserve(num_arcs as usize);
            }

            "n" => {
                let node_id: i32 = tokens[1].parse::<i32>()?;

                let supply_vals: Vec<i64> = tokens[3..].iter().map(|&t| t.parse::<i64>()).collect::<Result<Vec<_>, _>>()?;

                commodity_supply_demand_data.insert(node_id, supply_vals);

                if node_seen.insert(node_id) {
                    nodes.push(node_id);
                }
            }

            "a" => {
                let u: i32 = tokens[1].parse::<i32>()?;
                let v: i32 = tokens[2].parse::<i32>()?;
                let up: i32 = tokens[4].parse()?;

                let k = num_commodities as usize;
                let mut current_idx = 5;

                let parsed_caps: Vec<i64> = if rand_caps {
                    let res = tokens[current_idx..(current_idx + k)].iter().map(|&t| t.parse::<i64>()).collect::<Result<Vec<_>, _>>()?;
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

                edges.push((u, v));
                capacities.push(up);
                commodity_capacities.insert((u, v), parsed_caps);
                commodity_weights.insert((u, v), parsed_costs);
                start_nodes.push(u);
                end_nodes.push(v);
                
                for &node in &[u, v] {
                    if node_seen.insert(node) {
                        nodes.push(node);
                    }
                }
            }
            _ => {}
        }
    }

    let mut commodity_edges = Vec::with_capacity(num_commodities as usize * edges.len());
    for i in 0..num_commodities {
        for &(u, v) in &edges {
            commodity_edges.push((i, u, v));
        }
    }

    let mut commodity_bundle_capacities = Vec::with_capacity(num_commodities as usize * capacities.len());
    for _ in 0..num_commodities {
        commodity_bundle_capacities.extend_from_slice(&capacities);
    }

    Ok(ParsedMulticommodityInstance { 
        num_nodes: num_nodes, 
        num_arcs: num_arcs, 
        num_commodities: num_commodities as usize,
        randomized_capacities: rand_caps,
        randomized_weights: rand_costs, 
        nodes: nodes, 
        edges: edges, 
        commodity_supply_demand_data: commodity_supply_demand_data, 
        capacities: capacities, 
        commodity_capacities: commodity_capacities,
        commodity_weights: commodity_weights,
        commodity_edges: commodity_edges,
        commodity_bundle_capacities: commodity_bundle_capacities,
        start_nodes: start_nodes, 
        end_nodes: end_nodes, 
        is_uniform: is_uniform,
        seed: seed,
    })
}

pub fn export_to_dimacs(
    path: &str,
    instance: &NetworkInstance,
    multi_data: &MultiCommodityData,
) -> std::io::Result<()> {
    let file = File::create(path)?;
    let mut writer = BufWriter::new(file);

    let is_uniform_int = if multi_data.is_uniform { 1 } else { 0 };

    let write_seed = if multi_data.is_uniform && !multi_data.randomized_capacities && !multi_data.randomized_weights {
        0
    } else {
        multi_data.seed
    };
    
    // 1. Header
    writeln!(writer, "c Multicommodity flow generated by s2mflow")?;

    // 2. Problem Line: p min <nodes> <arcs> <commodities>
    let rand_caps_int = if multi_data.randomized_capacities { 1 } else { 0 };
    let rand_costs_int = if multi_data.randomized_weights { 1 } else { 0 };

    // p min num_nodes num_arcs num_commodities rand_caps rand_costs is_uniform seed
    writeln!(
        writer,
        "p min {} {} {} {} {} {} {}",
        instance.num_nodes,
        instance.num_arcs,
        multi_data.num_commodities,
        rand_caps_int,
        rand_costs_int,
        is_uniform_int,
        write_seed,
    )?;

    // 3. Node Lines: n <id> <total_supply> <c1> <c2> ...
    for (&node_id, supplies) in &multi_data.supply_partition {
        let total_supply: i32 = supplies.iter().sum();
        let supplies_str: Vec<String> = supplies.iter().map(|s| s.to_string()).collect();
        writeln!(writer, "n {} {} {}", node_id, total_supply, supplies_str.join(" "))?;
    }

    // 4. Arc Lines: a <tail> <head> <low> <upp> <cost_c1> <cost_c2> ...
    for (i, edge) in instance.edges.iter().enumerate() {
        let caps = &multi_data.capacites_by_arc[&i];
        let costs = &multi_data.weights_by_arc[&i];

        let caps_to_write = if multi_data.randomized_capacities { caps.as_slice() } else { &caps[0..1] };
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

pub fn get_incidence_mapping(
    nodes: Vec<i32>,
    edges: Vec<(i32, i32)>
) -> (BTreeMap<i32, Vec<i32>>, BTreeMap<i32, Vec<i32>>) {
    let mut incoming: BTreeMap<i32, Vec<i32>> = BTreeMap::new();
    let mut outgoing: BTreeMap<i32, Vec<i32>> = BTreeMap::new();

    for &node in &nodes {
        incoming.insert(node, Vec::new());
        outgoing.insert(node, Vec::new());
    }

    for (tail, head) in edges {
        incoming.get_mut(&head).unwrap().push(tail);
        outgoing.get_mut(&tail).unwrap().push(head);
    }

    (incoming, outgoing)
}