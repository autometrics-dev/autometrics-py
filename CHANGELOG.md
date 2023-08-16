# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

<!-- This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). -->

---

## [Unreleased]

### Added

- Added the `start_http_server`, which starts a separate HTTP server to expose
  the metrics instead of using a separate endpoint in the existing server. (#77)
- Added the `init` function that you can use to configure autometrics. (#77)

### Changed

- Renamed the `function.calls.count` metric to `function.calls` (which is exported
  to Prometheus as `function_calls_total`) to be in line with OpenTelemetry and
  OpenMetrics naming conventions. **Dashboards and alerting rules must be updated.** (#74)
- When the `function.calls.duration` histogram is exported to Prometheus, it now
  includes the units (`function_calls_duration_seconds`) to be in line with
  Prometheus/OpenMetrics naming conventions. **Dashboards and alerting rules must be updated.** (#74)
- The `caller` label on the `function.calls` metric was replaced with `caller.function`
  and `caller.module` (#75)
- All metrics now have a `service.name` label attached. This is set via runtime environment
  variable (`AUTOMETRICS_SERVICE_NAME` or `OTEL_SERVICE_NAME`), or falls back to the package name. (#76)

### Deprecated

-

### Removed

-

### Fixed

-

### Security

-

## [0.8](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.8) - 2023-07-24

### Added

- Support for prometheus-client 0.17.x

## [0.7](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.7) - 2023-07-19

### Added

- Initialize counter metrics at zero #54

### Changed

- Caller tracking only tracks autometricised functions, as per spec #59
- Function name labels now use qualified name, and module labels use module's `__name__` when available #59

### Deprecated

-

### Removed

-

### Fixed

- Fixed calculation of funciton duration when using OpenTelemetry tracker #66

### Security

-

## [0.6](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.6) - 2023-06-23

### Added

- Exemplars support (#51)
- Optional concurrency tracking support (#55)

### Changed

- `build_info` is extended with support for branch labels and now picks up the commit label from `COMMIT_SHA` env var (#52)

### Fixed

- Fixed decorator async function handling (#55)

### Security

- Update requests, starlette, fastapi dependencies used by the examples

## [0.5](https://github.com/autometrics-dev/autometrics-py/releases/tag/0.5) - 2023-05-11

### Added

- Support `build_info` metrics for Prometheus tracker (#35)
  - **NOTE**: The OpenTelemetry tracker does not accurately track `build_info`, so you will need to set the env var `AUTOMETRICS_TRACKER=PROMETHEUS` to see accurate build info in your metrics (see #38)
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
