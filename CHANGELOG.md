# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this

## [0.2.1] - 2026-09-05
### Added
- Added `cap_zero` and `cap_zero_param` parameters to `generate_multi_commodity_data`.
- Added zero-capacity arc exclusion logic: if `cap_zero=True` and `cap_zero_param > 0`, at least 
one arc per commodity is excluded.
- Added zero-capacity test coverage in Rust and Python test suites.

### Changed
- Updated `.mcfmin` format to store `cap_zero` and `cap_zero_param` in the problem line.
- Updated documentation, type stubs, and examples to reflect the zero-capacity feature.

## [0.2.0] - 2026-08-27
### Added
- Added `split_supplies_beta_binomial` for beta-binomial integer partitioning with concentration parameter.
- Added `compute_commodity_demand_heterogeneity` to compute the Commodity-Demand Heterogeneity metric H(B).

### Changed
- Replaced the `is_uniform` boolean argument with a `method` integer parameter in `generate_multi_commodity_data` and related functions. Methods: `0` = Spread, `1` = Uniform, `2` = Beta-Binomial.
- Updated the `.mcfmin` format to store `method` instead of `is_uniform` in the problem line.
- Modified the global balancing phase to randomly select the surplus commodity for stochastic methods (Spread and Beta-Binomial), while keeping Uniform deterministic.
- Updated all tests, documentation, and example scripts to reflect the new API and features.

## [0.1.22] - 2026-07-11
### Changed
- Updated `CITATION.cff` and `README.md` with *SoftwareX* publication details.

## [0.1.21] - 2026-06-21
### Changed
- Minor fix in `README.md`.

## [0.1.20] - 2026-06-21
### Added
- Added end-to-end optimization workflows (`examples/solve_instance_pyomo.py` and `examples/solve_instance_gurobi.py`).

### Changed
- Expanded `readthedocs` documentation with comprehensive API references, setup guide, and workflows.
- Extended `README.md` with setup guide, workflows, and scalability benchmark results.

## [0.1.19] - 2026-05-26
### Changed
- Changed method to `get_adjacency_mapping`.

## [0.1.18] - 2026-05-26
### Changed
- Updated `s2mflow.pyi`.

## [0.1.17] - 2026-05-26
### Changed
- Updated documentation.

## [0.1.16] - 2026-05-26
### Changed
- Renamed `num_k` to `num_commodities` in `split_supplies_uniform` and `split_supplies_spread` for consistency in API.

## [0.1.15] - 2026-05-24
### Added
- Added `examples/demo.py`.
- Added `Building from Source` in `README.md`.

## [0.1.14] - 2026-05-23
### Added
- CI/CD Pipeline: Integrated GitHub Actions (`ci.yml`) to automate testing for both the native Rust core and Python API.
- Added repository badges to `README.md`.

## [0.1.13] - 2026-05-19
### Changed
- Unified the core data layer to `i64` for type-safety and overflow prevention.

### Added
- Added a root-level `data/` directory with sample instances.
- Added Rust integration tests (`test_round_trip` and `test_partition_logic`).

## [0.1.12] - 2026-05-18
### Added
- Added testing infrastructure for multicommodity data generation (`test_partition_logic`).
- Added end-to-end file round-trip test (`test_round_trip`).

## [0.1.11] - 2026-05-17
### Fixed
- Fixed CI.

## [0.1.10] - 2026-05-17
### Fixed
- `src/utils.rs`: fixed bug inside the multicommodity parser.

## [0.1.9] - 2026-05-16
### Added
- Upgraded to **Rust Edition 2024**.

### Fixed
- Inside `.github/workflows/release.yml`: directory tracking path masks (`dist/*.whl` and `dist/*.tar.gz`).

## [0.1.8] - 2026-05-06
### Added
- Added basic tests.

## [0.1.7] - 2026-04-06
### Changed
- Adjusted `README.md` and citation.

## [0.1.6] - 2026-03-29
### Changed
- Documentation.

## [0.1.5] - 2026-03-29
### Added
- Integrated **Sphinx** documentation with the Read the Docs theme.

### Changed
- Added documentation dependencies in `dev` group in `pyproject.toml`.

## [0.1.4] - 2026-03-29
### Fixed
- Adjusted citation reference: removed version.

## [0.1.3] - 2026-03-29
### Fixed
- Corrected "MIT License" typo in `README.md`.

## [0.1.2] - 2026-03-29
### Fixed
- Refined definitions for `uniform` and `spread` partitioning logic.
- Corrected `README.md`.

## [0.1.1] - 2026-03-29
### Fixed
- Updated license information.
- Fixed minors in `README.md`.

## [Unreleased]

## [0.1.0] - 2026-03-28
### Added
- **Core Rust Engine**: Implementation for multicommodity flow instance generation.
- **Python Bindings**: Integration using PyO3 and Maturin.
- **Instance Loading**: Support for reading single-commodity `.min` files and multicommodity `.mcfmin` (introduced format) files.
- **Instance Writing**: Support for writing multicommodity files to `.mcfmin` format.
- **Utils**: Support for identifying incoming and outgoing edges.
- **Partitioning Strategies**:
    - `split_supplies_uniform`.
    - `split_supplies_spread`.
- **CI/CD Pipeline**: Automated multi-platform builds (Linux, Windows, maxOS) via GitHub Actions.

