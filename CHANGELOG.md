# Changelog

## [Unreleased]
### Added
- New features or functionalities added to the project.

### Changed
- Updates or modifications to existing features.

### Fixed
- Bug fixes or corrections to existing issues.

### Removed
- Features or functionalities that have been removed.

## [v1.2.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.2.0) - 2025-09-18
### Added
- Added support for the new [collections API](https://docs.x.ai/docs/guides/using-collections)
- Added a new `collections` sub-client to `Client` and `AsyncClient` which can be used to interact with the collections API.
- The `Client` and `AsyncClient` objects now accept an optional `management_api_key` parameter which can be used to authenticate requests to the management API (e.g. CRUD operations on collections). Alternatively, the `XAI_MANAGEMENT_API_KEY` environment variable can be used to set this value without having to pass it as a parameter.
- Added support for the new [stateful chat API](https://docs.x.ai/docs/guides/responses-api)
- Added two new parameters to the `chat.create` method:
    - `store_messages` whether to persist messages on xAI servers such that they can be referenced and retrieved later.
    - `previous_response_id` allows you to specify the ID of a previously stored response to use as the starting point for the new chat.
- Added two new methods to the `chat` object:
    - `get_stored_completion` allows you to retrieve a previously stored response by its ID.
    - `delete_stored_completion` allows you to delete a previously stored response by its ID.

### Removed
- **Breaking Change**: Removed the `documents` sub-client from `Client` and `AsyncClient`. In order to search for documents within collections, use the `client.collections.search` method instead.

## [v1.1.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.1.0) - 2025-08-21
### Added
- Added OpenTelemetry integration for distributed tracing and monitoring of SDK operations
- Instrumented all methods that make gRPC requests to produce spans with relevant request/response attributes closely adhering to the OpenTelemetry GenAI Semantic Conventions.
- Added a new `telemetry` module (`xai_sdk.telemetry`) which can be used to setup trace creation and exporting of traces to an otel backend or to the console
- Added a new `documents` sub-client to `Client` and `AsyncClient` which can be used to interact with the documents API.
- Added a new `search` method on the `documents` sub-client which can be used to perform semantic search for documents that are stored in collections.

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