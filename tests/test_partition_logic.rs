use std::path::{Path, PathBuf};
use s2mflow::{load_min_instance, generate_multi_commodity_data};

#[test]
fn test_partition_logic() {
    let data_dir_env = std::env::var("S2MFLOW_DATA_DIR").unwrap_or_else(|_| "data".to_string());
    let data_dir = PathBuf::from(data_dir_env);

    if !data_dir.exists() {
        println!("cargo:warning=Data directory not found.");
        return;
    }

    let mut min_files = Vec::new();
    fn find_min_files_recursive(dir: &Path, files: &mut Vec<PathBuf>) {
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

    let num_commodities_space = vec![2, 3, 5, 10];
    let is_uniform_space = vec![true, false];
    let seed = 42;

    let mut failed_cases = Vec::new();

    for file_path in &min_files {
        let file_name = file_path.file_name().unwrap().to_str().unwrap().to_string();
        let network = load_min_instance(file_path.to_str().unwrap().to_string()).unwrap();

        for &num_commodities in & num_commodities_space {
            for &is_uniform in &is_uniform_space {

                let case_context = format!(
                    "File: {}, K: {}, Uniform: {}",
                    file_name, num_commodities, is_uniform
                );

                println!("Testing Partition Logic: {}", case_context);

                let result = std::panic::catch_unwind(|| {
                    let mc_data = generate_multi_commodity_data(
                        &network, 
                        num_commodities, 
                        is_uniform, 
                        false, 
                        1.0, 
                        1.0, 
                        false, 
                        1.0, 
                        1.0, 
                        seed
                    );

                    // Local Balance and Sign Consistency Checks
                    for (&node_id, partitioned_vals) in &mc_data.supply_partition {
                        let original_supply = *network.supplies.get(&node_id).unwrap_or(&0i64);
                        
                        // Local Partitioning: sum_k(b_i^k) == b_i for each i
                        let local_sum: i64 = partitioned_vals.iter().sum();
                        assert_eq!(
                            local_sum, 
                            original_supply,
                            "Local balance broken at node {}. Got sum={}, expected={} ({})",
                            node_id, local_sum, original_supply, case_context
                        );
                        
                        for &val in partitioned_vals {
                            if original_supply > 0 {
                                assert!(
                                    val >= 0,
                                    "Sign violation: Postive supply node {} generated negative partition value {} ({}).",
                                    node_id, val, case_context
                                );
                            } else if original_supply < 0 {
                                assert!(
                                    val <= 0,
                                    "Sign violation: Negative demand node {} generated positive partition value {} ({}).",
                                    node_id, val, case_context
                                );
                            }
                        }
                    }

                    // Global Balance Check: sum_i(b_i^k) == 0 for rach k.
                    for k in 0..num_commodities {
                        let mut commodity_global_sum: i64 = 0;

                        for node_vals in mc_data.supply_partition.values() {
                            commodity_global_sum += node_vals[k];
                        }

                        assert_eq!(
                            commodity_global_sum, 0,
                            "Global conservation borken for commodity index {}! Summed nodes total was {} ({}).",
                            k, commodity_global_sum, case_context
                        );
                    }

                });

                if result.is_err() {
                    failed_cases.push(case_context);
                }

            }
        }

    }

    if !failed_cases.is_empty() {
        println!("\n {} Partition Logic Test Failed:", failed_cases.len());
        for case in &failed_cases {
            println!("  > {}", case);
        }
        panic!("Partition logic testing suite failed.");
    } else {
        println!("\n Partition logic test passed perfectly.")
    }

}