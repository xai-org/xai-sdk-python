# Changelog

## [Unreleased]

## [v1.6.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.6.0) - 2026-01-27
### Added
- **Batch API**: Added new `client.batch` sub-client for interacting with the Batch API:
    - Ability to create, manage, and retrieve batch jobs
    - Integration with existing chat objects when adding requests to a batch
    - New optional `batch_request_id` field in `chat.create` method
- **Developer Role**: Added `developer` role support for chat messages with `developer()` utility function
- **Tool Call ID Field**: Added `tool_call_id` field and argument to `tool_result` utility function for explicit tool call identification
- **User Location for Web Search**: Added user-location support to `web_search()` server-side tool with new location-related arguments

### Changed
- **Telemetry Improvements**:
    - Updated chat spans to be compliant with latest OpenTelemetry `gen_ai` semantic conventions
    - Now emits `xai` under `gen_ai.provider.name` field instead of `gen_ai.system`
    - Added `server.address` attribute set to `api.x.ai`
    - Added instrumentation for Files API methods (`upload`, `delete`)
    - Added instrumentation for Collections API methods (`create`, `update`, `delete`, `upload_document`, `add_existing_document`, `remove_document`, `update_document`)

## [v1.5.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.5.0) - 2025-12-04
### Added
- **Server-Side Tool Output Utilities**: Added utility functions to retrieve server-side tool call outputs from responses
- **Collections API Enhancements**:
    - Added `field_definitions` parameter to `collections.create()` enabling custom document metadata schemas with validation constraints (`required`, `unique`, `inject_into_chunk`)
    - Added `metric_space` parameter to `collections.create()` supporting HNSW distance metrics (`cosine`, `euclidean`, `inner_product`)
    - Added `filter` parameter to `collections.list()` with support for filtering by `collection_name`, `created_at`, and `documents_count`
    - Added `wait_for_indexing` parameter to document upload with customizable `poll_interval` and `timeout`
    - Added `instructions` and `retrieval_mode` parameters to `collections.search()`
    - Implemented dict-based `TypedDict` interfaces as ergonomic alternatives to protobuf objects
- **Inline Citations**: Added property methods for convenient access to inline citations on responses for both streaming and unary responses
    - Added `end_index` field for `InlineCitation`
- **Verbose Streaming**: Added `verbose_streaming` to include options for streaming responses

### Changed
- Renamed built-in document search tool to "attachment search" for clarity
- Collections `upload_document` now streams bytes via the Files `UploadFile` endpoint, then attaches the resulting file to the collection

### Removed
- **Breaking Change**: The `content_type` parameter was removed from the public `collections.upload_document` function

## [v1.4.1](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.4.1) - 2025-11-26
### Added
- **Tool Call Status Tracking**: Added status field to tool call entries in chat response outputs for tracking tool execution progress
    - Tool call messages now include a status field indicating the current state of the tool call
    - Multiple entries for the same tool call can now represent different stages (in progress, success, failure)
    - Enables real-time tracking of server-side tool execution lifecycle
- **Batch File Upload**: Added `batch_upload` method to both sync and async file clients for concurrent uploads of multiple files with progress tracking
- **Max Turns Parameter**: Added `max_turns` parameter to `chat.create` for configuring the maximum number of agentic turns when using server-side tools
- **Include Field**: Added `include` field to chat requests allowing users to specify optional outputs to be returned (e.g., tool output, inline citations)
- **Inline Citations**: Added `InlineCitation` support for agentic search outputs
- **Model Literals**: Introduced `Model` literals for type-safe model specification and editor autocomplete support

### Changed
- Reorganized existing literals into the `types` folder for better organization
- Updated gRPC metadata to include the language (Python) alongside SDK version

## [v1.4.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.4.0) - 2025-11-07
### Added
- **Files API**: Added support for the [Files API](https://docs.x.ai/docs/guides/files) with new `client.files` sub-client for uploading and managing files
- **Remote MCP Tools**: Added support for [remote MCP](https://docs.x.ai/docs/guides/tools/remote-mcp-tools) (Model Context Protocol) tool integration, enabling connection to external MCP servers
- **Collections Search Tool**: Added [collections-search](https://docs.x.ai/docs/guides/tools/collections-search-tool) as a server-side tool with proto support and convenience utility functions
- **Structured Outputs Enhancement**: Allow passing a Pydantic `BaseModel` directly to `response_format` parameter in `chat.create` for type-safe structured outputs
- **Client Resource Management**: Added context manager support and explicit `close()` methods to `Client` and `AsyncClient` for proper gRPC channel cleanup
- **Chat Response Features**:
    - Added support for encrypted content in chat responses
    - Added debug output support in chat responses
- **Tool Enhancements**:
    - Added `SERVER_SIDE_TOOL_MCP` and `SERVER_SIDE_TOOL_COLLECTIONS_SEARCH` to `ServerSideTool` usage enum
    - Added `ToolCallType` support in `ToolCall` for distinguishing between client-side and server-side tools
    - Added utility function `get_tool_call_type()` for retrieving tool call types
    - Added new examples for MCP and collections search server-side tools
- **Client Configuration**:
    - Added option to use an insecure gRPC channel via `insecure` parameter (useful for local development)
    - Added `xai-sdk-version` metadata header to all gRPC requests for better debugging and analytics
- **Telemetry Controls**: Added ability to exclude sensitive attributes from telemetry spans/traces via the `XAI_SDK_DISABLE_SENSITIVE_TELEMETRY_ATTRIBUTES` environment variable

### Changed
- Optimized streaming chat response memory usage with lazy buffering
- Renamed internal `ChoiceChunk` class to `CompletionOutputChunk`
- Improved agentic response handling to append all output entries correctly
- Set index correctly in `parse` method for chat responses

### Fixed
- Removed double await in `UnaryStreamAioInterceptor`

## [v1.3.1](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.3.1) - 2025-10-17
### Fixed
- Fixed handling of multi-output responses in agentic workflows (server-side tools). When server-side tools are used, the API returns multiple completion outputs in a single response (tool call → tool result → final answer). This release ensures:
    - `response.tool_calls` now correctly returns ALL tool calls from all assistant outputs in the response, not just those from a single output index
    - `response.content` properly aggregates and returns the final assistant response content
    - Streaming chunks correctly expose all assistant outputs during agentic multi-turn conversations
    - All outputs are properly tracked and indexed, preventing missing tool calls or incomplete responses

## [v1.3.0](https://github.com/xai-org/xai-sdk-python/releases/tag/v1.3.0) - 2025-10-15
### Added
- Added proto support for three new server-side tools in agentic workflows:
    - `web_search()`: Enables web search with configurable domain filtering (exclude/allow lists) and image understanding capabilities
    - `x_search()`: Enables X (Twitter) search with date range filtering, handle-based filtering (include/exclude), and both image and video understanding
    - `code_execution()`: Enables server-side code execution for computational tasks
- Added convenience functions in new `xai_sdk.tools` module for easily creating server-side tool configurations
- Added `ServerSideTool` enum in usage proto for tracking server-side tool usage (WEB_SEARCH, X_SEARCH, CODE_EXECUTION, VIEW_IMAGE, VIEW_X_VIDEO)
- Added `server_side_tools_used` field to `SamplingUsage` for detailed usage tracking of which server-side tools were invoked

### Changed
- **Breaking Proto Change**: Renamed response structure fields for semantic clarity and better multi-output support:
    - `GetChatCompletionResponse.choices` → `GetChatCompletionResponse.outputs` 
    - `GetChatCompletionChunk.choices` → `GetChatCompletionChunk.outputs`
    - `Choice` message type → `CompletionOutput`
    - `ChoiceChunk` message type → `CompletionOutputChunk`
    - This change better reflects the API's capability to return multiple completion outputs rather than "choices," providing clearer semantics for the response structure

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