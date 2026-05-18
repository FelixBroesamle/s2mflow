use s2mflow::load_min_instance;

/// 1. Smoke test to verify the library links and can be invoked.
#[test]
fn test_package_linkage() {
    let result = load_min_instance("".to_string());
    assert!(result.is_err());
}

/// 2. Deliberate failure test to verify that cargo test assertion framework behaves correctly when a panic is triggered.
#[test]
#[should_panic(expected = "Deliberate failure to verify assertion framework behavior.")]
fn test_expected_fail() {
    panic!("Deliberate failure to verify assertion framework behavior.");
}
