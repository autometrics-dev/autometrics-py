# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

<!-- This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). -->

---

## [Unreleased]

### Added

-

### Changed

-

### Deprecated

-

### Removed

-

### Fixed

### Security

- ***

## [0.5](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.5) - 2023-05-11

### Added

- Support for build_info metrics in Prometheus (#35)
- OpenTelemetry Support (#28)
- Fly.io example (#26)
- Django example (#22)

### Fixed

- The `autometrics` decorator now supports async functions (#33)

## [0.4](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.4) - 2023-04-13

### Added

- SLO Support (#16)
- Improved documentation and examples (#13 #19)

### Changed

- Development setup (#10 #12)

### Fixed

- Issue with trailing slashes in prometheus url (#14)

## [0.3](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.3) - 2023-03-28

### Added

- Implemented caller label for the function calls counter (#9)
