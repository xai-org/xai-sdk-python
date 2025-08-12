# Changelog

## [Unreleased]
### Added
- Added OpenTelemetry integration for distributed tracing and monitoring of SDK operations
- Instrumented all methods that make gRPC requests to produce spans with relevant request/response attributes
- Added a new `telemetry` module (`xai_sdk.telemetry`) which can be used to setup trace creation and exporting of traces to an otel backend or to the console

### Changed
- Updates or modifications to existing features.

### Fixed
- Bug fixes or corrections to existing issues.

### Removed
- Features or functionalities that have been removed.

## [v1.0.1](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.0.1) - 2025-07-22
### Fixed
- Fixed a bug that caused the `from_date` and `to_date` parameters to have no effect when using them via `SearchParameters` for the live search feature
    
## [v1.0.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.0.0) - 2025-07-02
### Added
- Added support for new parameters to the `x_source` (`from xai_sdk.search import x_source`) for use with the live search API feature:
    - `included_x_handles` allows you to limit posts used to those only authored by particular handles
    - `excluded_x_handles` allows you to exclude posts authored by particular handles
    - `post_favorite_count` allows you to set a threshold for the minimum number of favorites a post must have to be considered
    - `post_view_count` allows you to set a threshold for the minimum number of views a post must have to be considered


## [v1.0.0rc2](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.0.0rc2) - 2025-06-26
### Fixed
- Fixed an issue where long running gRPC requests would prematurely terminate.

## [v1.0.0rc1](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.0.0rc1) - 2025-06-13
### Added
- Initial RC version of the xai-sdk