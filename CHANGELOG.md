# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## v3.0.0

### Changed
- Implement global command-line tool `facile-rs` to replace direct call to the different scripts.
- Documentation files gathered in the ReadTheDocs documentation

### Added
- Add CI/CD template repository

## v2.2.0

### Changed
- Remove variable `PUSH_TOKEN` from CI pipeline, use `PRIVATE_TOKEN` instead.

### Added
- Add feature for archiving on Zenodo via the scripts `prepare_zenodo.py` and `create_zenodo.py`
- Workflow for publishing releases on PyPI and integrating the Python wheel to the GitLab release.

### Fixed
- Consequently remove SPDX URL from RADAR license metadata

## v2.1.0

### Added
- Create pytest test suite for metadata conversion
- Add CI job for pytest
- Support 'funder' keyword in CodeMeta
- Auto-generated documentation using Sphinx

### Fixed
- Fix prefix replacements in strings in CFF conversion
- Handle CodeMeta schema for funding metadata
- Support CodeMeta or Schema.org metadata values being single elements and not lists

## v2.0.0

### Changed
- Fix `false` to `False` in `prepare_radar.py`
- Calling citeproc with `--citeproc instead` of as a filter
- Rename openCARP-CI to FACILE-RS
- FACILE-RS now requires Python>=3.8
- Use Python 3.11 in CI

### Added
- Add pyproject.toml

### Fixed
- Correctly parse `@type` when converting to RADAR metadata
- Remove `https://spdx.org/licenses/` from license name for RADAR and CFF

## v1.5.2

### Changed
- Fix "publishers" field in RADAR metadata

### Added
- Activate RADAR CI jobs

## v1.5.1

### Added
- thumbnails in the docstring pipeline are now automatically generated
- added the CI pipelines
- initialise the CHANGELOG.md
