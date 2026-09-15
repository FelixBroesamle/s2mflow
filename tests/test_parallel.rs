use std::collections::BTreeSet;
use std::path::PathBuf;
use s2mflow::{
    load_min_instance,
    load_multi_commodity_instance,
    save_multi_commodity_instance,
    generate_multi_commodity_data,
    MultiCommodityData,
    NetworkInstance
};

const SMALL: &str = "\
p min 3 4
n 1 10
n 3 -10
a 1 2 0 6 3
a 1 2 0 4 2
a 2 3 0 10 1
a 1 3 0 10 5
";
const SEQ: &str = "p min 2 1\nn 1 5\nn 2 -5\na 1 2 0 5 1\n";

fn write(name: &str, content: &str) -> PathBuf {
    let p = std::env::temp_dir().join(name);
    std::fs::write(&p, content).unwrap();
    p
}

fn gridgen_path() -> Option<PathBuf> {
    let env = std::env::var("S2MFLOW_DATA_DIR").unwrap_or_else(|_| "data".to_string());
    let p = PathBuf::from(env).join("gridgen_1").join("smcg_gridgen_1.min");
    p.exists().then_some(p)
}

fn load_gridgen() -> Option<NetworkInstance> {
    gridgen_path().map(|p| load_min_instance(p.to_str().unwrap().to_string()).unwrap())
}

fn assert_unique_keys(md: &MultiCommodityData, num_arcs: i64) {
    let n = num_arcs as usize;
    assert_eq!(md.capacities_by_arc.len(), n);
    assert_eq!(md.weights_by_arc.len(), n);
    assert_eq!(md.commodity_capacities.len(), n);
    assert_eq!(md.commodity_weights.len(), n);
}

#[test]
fn small_parallel_parse() {
    let p = write("s2mflow_small_par.min", SMALL);
    let net = load_min_instance(p.to_str().unwrap().to_string()).unwrap();
    assert!(net.parallel);
    assert_eq!(net.num_parallel_arc_pairs, 1);
    assert_eq!(net.arcs, vec![(1, 2, 0), (1, 2, 1), (2, 3, 0), (1, 3, 0)]);
    assert_eq!(net.arc_indices[&(1, 2)], vec![0usize, 1]);
}

#[test]
fn small_sequential_parse() {
    let p = write("s2mflow_small_seq.min", SEQ);
    let net = load_min_instance(p.to_str().unwrap().to_string()).unwrap();
    assert!(!net.parallel);
    assert_eq!(net.arcs, vec![(1, 2, 0)]);
    assert!(net.edges.iter().all(|e| e.index == 0));
}

#[test]
fn small_parallel_generate_and_round_trip() {
    let p = write("s2mflow_small_par.min", SMALL);
    let net = load_min_instance(p.to_str().unwrap().to_string()).unwrap();

    let md = generate_multi_commodity_data(
        &net, 3, 0,
        true, 0.7, 1.0,
        true, 0.8, 1.2,
        3.0, false, 0.0, 42,
    );
    assert_unique_keys(&md, net.num_arcs);
    assert_eq!(md.commodity_edges.len(), 3 * net.num_arcs as usize);

    let out = std::env::temp_dir().join("s2mflow_small_par.mcfmin");
    save_multi_commodity_instance(out.to_str().unwrap().to_string(), &net, &md).unwrap();
    let ld = load_multi_commodity_instance(out.to_str().unwrap().to_string()).unwrap();

    assert!(ld.parallel);
    assert_eq!(ld.edges, net.arcs);
    assert_unique_keys(&md, net.num_arcs);

    for (i, &(u, v, idx)) in ld.edges.iter().enumerate() {
        assert_eq!(ld.commodity_capacities[&(u, v, idx)], md.capacities_by_arc[&i]);
        assert_eq!(ld.commodity_weights[&(u, v, idx)],    md.weights_by_arc[&i]);
    }
    let _ = std::fs::remove_file(out);
}

#[test]
fn incidence_mapping() {
    let p = write("s2mflow_small_par.min", SMALL);
    let net = load_min_instance(p.to_str().unwrap().to_string()).unwrap();

    let (in_arcs, out_arcs) =
        s2mflow::get_incidence_mapping(net.nodes.clone(), net.arcs.clone());

    assert_eq!(out_arcs[&1], vec![(1, 2, 0), (1, 2, 1), (1, 3, 0)]);
    assert_eq!(in_arcs[&2],  vec![(1, 2, 0), (1, 2, 1)]);
    assert_eq!(in_arcs[&3],  vec![(2, 3, 0), (1, 3, 0)]);
    assert!(out_arcs[&3].is_empty());
    assert!(in_arcs[&1].is_empty());
}

#[test]
fn gridgen_parse_integrity() {
    let Some(net) = load_gridgen() else { return };

    assert!(net.parallel);
    assert!(net.num_parallel_arc_pairs > 0);
    assert_eq!(net.num_arcs as usize, net.edges.len());
    assert_eq!(net.arcs.len(), net.edges.len());

    // Every arc appears exactly once across all (tail, head) groups.
    let total: usize = net.arc_indices.values().map(|v| v.len()).sum();
    assert_eq!(total, net.num_arcs as usize);

    // Within each group the parallel indices form a contiguous 0..n-1 sequence.
    for positions in net.arc_indices.values() {
        let mut idxs: Vec<i64> = positions.iter().map(|&p| net.edges[p].index).collect();
        idxs.sort();
        assert_eq!(idxs, (0..positions.len() as i64).collect::<Vec<_>>());
    }

    // The (tail, head, index) triple is injective over arcs.
    let mut triples = BTreeSet::new();
    for &(u, v, i) in &net.arcs {
        assert!(triples.insert((u, v, i)), "duplicate triple ({u}, {v}, {i})");
    }
}

#[test]
fn gridgen_generate_unique_keys() {
    let Some(net) = load_gridgen() else { return };

    for k in [2usize, 5, 10] {
        let md = generate_multi_commodity_data(
            &net, k, 0,
            true, 0.7, 1.0,
            true, 0.8, 1.2,
            3.0, false, 0.0, 42,
        );
        assert_unique_keys(&md, net.num_arcs);
        assert_eq!(md.commodity_edges.len(), k * net.num_arcs as usize);

        // Every 4-tuple references a real arc, and its `idx` matches the arc at that position.
        for (kk, u, v, idx) in &md.commodity_edges {
            assert!(*kk < k);
            let positions = &net.arc_indices[&(*u, *v)];
            // There must be exactly one position p with edges[p].index == idx.
            assert_eq!(
                positions.iter().filter(|&&p| net.edges[p].index == *idx).count(),
                1,
                "no unique arc at ({u}, {v}, {idx})"
            );
        }
    }
}

#[test]
fn gridgen_round_trip_full() {
    let Some(net) = load_gridgen() else { return };

    let md = generate_multi_commodity_data(
        &net, 3, 0,
        true, 0.7, 1.0,
        true, 0.8, 1.2,
        3.0, false, 0.0, 7,
    );
    let out = std::env::temp_dir().join("s2mflow_gridgen_rt.mcfmin");
    save_multi_commodity_instance(out.to_str().unwrap().to_string(), &net, &md).unwrap();
    let ld = load_multi_commodity_instance(out.to_str().unwrap().to_string()).unwrap();

    assert!(ld.parallel);
    assert_eq!(ld.edges, net.arcs);
    assert_eq!(ld.arc_indices, net.arc_indices);
    assert_unique_keys(&md, net.num_arcs);

    for (i, &(u, v, idx)) in ld.edges.iter().enumerate() {
        assert_eq!(ld.commodity_capacities[&(u, v, idx)], md.capacities_by_arc[&i]);
        assert_eq!(ld.commodity_weights[&(u, v, idx)],    md.weights_by_arc[&i]);
    }
    let _ = std::fs::remove_file(out);
}


