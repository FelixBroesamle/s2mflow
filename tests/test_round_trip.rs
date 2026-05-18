use std::path::PathBuf;
use s2mflow::{
    load_min_instance,
    generate_multi_commodity_data,
    save_multi_commodity_instance,
    load_multi_commodity_instance,
};

#[test]
fn test_round_trip() {
    let data_dir_env = std::env::var("S2MFLOW_DATA_DIR").unwrap_or_else(|_| "../s2mflow_data".to_string());
    let data_dir = PathBuf::from(data_dir_env);

    if !data_dir.exists() {
        println!("cargo:warning=Data directory not found.");
        return;
    }

    let mut min_files = Vec::new();

    fn find_min_files_recursive(dir: &std::path::Path, files: &mut Vec<std::path::PathBuf>) {
        if let Ok(entries) = std::fs::read_dir(dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_dir() {
                    find_min_files_recursive(&path, files);
                } else if path.extension().map_or(false, |ext| ext == "min") {
                    files.push(path);
                }
            }
        }    
    }

    find_min_files_recursive(&data_dir, &mut min_files);

    assert!(!min_files.is_empty(), "No .min instances found inside s2mflow_data.");

    // parameter spaces
    let num_commodities_space = vec![2, 3, 5];
    let is_uniform_space = vec![true, false];
    let randomize_caps_space = vec![true, false];
    let randomize_costs_space = vec![true, false];

    let temp_dir = std::env::temp_dir();
    let seed = 42;

    let mut failed_cases = Vec::new();

    for file_path in &min_files {
        let file_name = file_path.file_name().unwrap().to_str().unwrap().to_string();
   
        let network = load_min_instance(file_path.to_str().unwrap().to_string()).unwrap();

        for &num_commodities in &num_commodities_space {
            for &is_uniform in &is_uniform_space {
                for &rand_caps in &randomize_caps_space {
                    for &rand_costs in &randomize_costs_space {

                        let case_context = format!(
                            "File: {}, K: {}, Uniform: {}, rand_caps: {}, rand_costs: {}",
                            file_name, num_commodities, is_uniform, rand_caps, rand_costs
                        );

                        let result = std::panic::catch_unwind(|| {
                            let generated = generate_multi_commodity_data(
                                &network, 
                                num_commodities, 
                                is_uniform, 
                                rand_caps, 
                                0.8, 
                                1.2, 
                                rand_costs, 
                                0.8, 
                                1.2, 
                                seed
                            );

                            let out_name = format!("rt_{}_{}_{}_{}_{}.mcfmin", file_name, num_commodities, is_uniform, rand_caps, rand_costs);
                            let output_path = temp_dir.join(out_name);
                            let output_path_str = output_path.to_str().unwrap().to_string();

                            save_multi_commodity_instance(output_path_str.clone(), &network, &generated).unwrap();

                            let loaded = load_multi_commodity_instance(output_path_str.clone()).unwrap();   

                            // Check 1:
                            assert_eq!(loaded.num_nodes, network.num_nodes);
                            assert_eq!(loaded.num_arcs, network.num_arcs);
                            assert_eq!(loaded.num_commodities, num_commodities);
                            assert_eq!(loaded.randomized_capacities, rand_caps);
                            assert_eq!(loaded.randomized_weights, rand_costs);
                            assert_eq!(loaded.is_uniform, is_uniform);

                            let expected_seed = if is_uniform && !rand_caps && !rand_costs { 0 } else { seed };
                            assert_eq!(loaded.seed, expected_seed);

                            for (node_id, gen_vals) in &generated.supply_partition {
                                let loaded_vals = loaded.commodity_supply_demand_data.get(node_id).expect(&format!("Missing node key: {}", node_id));
                                assert_eq!(loaded_vals, gen_vals);
                            }

                            for (i, edge) in network.edges.iter().enumerate() {
                                let arc_key = (edge.tail, edge.head);

                                let loaded_cap = loaded.commodity_capacities.get(&arc_key).expect(&format!("Arc key weight missing: {:?}", arc_key));
                                assert_eq!(loaded_cap, &generated.capacites_by_arc[&i]);

                                let loaded_weight = loaded.commodity_weights.get(&arc_key).expect(&format!("Arc key wieght missing: {:?}", arc_key));
                                assert_eq!(loaded_weight, &generated.weights_by_arc[&i]);
                            }

                            let _ = std::fs::remove_file(output_path);

                        });

                        if result.is_err() {
                            failed_cases.push(case_context);
                        }
                    }
                }
            }
        }
    }

    if !failed_cases.is_empty() {
        println!("\n {} Cases Failed:", failed_cases.len());
        for case in &failed_cases {
            println!("  > {}", case);
        }
        panic!("Rount-trip suite failed.")
    } else {
        println!("Round-trip test passed perfectly.")
    }

}