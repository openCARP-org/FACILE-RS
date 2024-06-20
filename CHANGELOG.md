# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

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
- intialise the CHANGELOG.md
