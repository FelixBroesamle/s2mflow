# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this

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

