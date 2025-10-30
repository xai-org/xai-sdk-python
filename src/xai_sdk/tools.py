import datetime
from typing import Optional

from google.protobuf.timestamp_pb2 import Timestamp

from xai_sdk.proto import chat_pb2


def web_search(
    excluded_domains: Optional[list[str]] = None,
    allowed_domains: Optional[list[str]] = None,
    *,
    enable_image_understanding: bool = False,
) -> chat_pb2.Tool:
    """Creates a server-side tool for web search, typically used in agentic requests.

    This tool enables the model to perform web searches and access online content during
    conversation. It can be configured to restrict or exclude specific domains and enable
    image understanding capabilities.

    Args:
        excluded_domains: List of website domains (without protocol specification or subdomains)
            to exclude from search results (e.g., ["example.com"]). Use this to prevent results
            from unwanted sites. A maximum of 5 websites can be excluded. This parameter
            cannot be set together with `allowed_domains`.
        allowed_domains: List of website domains (without protocol specification or subdomains)
            to restrict search results to (e.g., ["example.com"]). A maximum of 5 websites can be
            allowed. Use this as a whitelist to limit results to only these specific sites; no
            other websites will be considered. This parameter cannot be set together with `excluded_domains`.
        enable_image_understanding: Enables understanding/interpreting images encountered during the web search process.

    Returns:
        A `chat_pb2.Tool` object configured for web search.

    Example:
        ```
        from xai_sdk.tools import web_search

        # Create a web search tool that excludes certain domains
        tool = web_search(
            excluded_domains=["spam-site.com", "unwanted.com"],
            enable_image_understanding=True
        )
        ```
    """
    return chat_pb2.Tool(
        web_search=chat_pb2.WebSearch(
            excluded_domains=excluded_domains,
            allowed_domains=allowed_domains,
            enable_image_understanding=enable_image_understanding,
        )
    )


def x_search(
    from_date: Optional[datetime.datetime] = None,
    to_date: Optional[datetime.datetime] = None,
    allowed_x_handles: Optional[list[str]] = None,
    excluded_x_handles: Optional[list[str]] = None,
    *,
    enable_image_understanding: bool = False,
    enable_video_understanding: bool = False,
) -> chat_pb2.Tool:
    """Creates a server-side tool for X (Twitter) search, typically used in agentic requests.

    This tool enables the model to search X (formerly Twitter) posts and access social media
    content during conversation. It can be configured with date ranges, user handle filters,
    and media understanding capabilities.

    Args:
        from_date: Optional start date for search results. Only content after this date
            will be considered. Defaults to None (no start date restriction).
        to_date: Optional end date for search results. Only content before this date
            will be considered. Defaults to None (no end date restriction).
        allowed_x_handles: Optional list of X usernames (without the '@' symbol) to limit
            search results to posts from specific accounts (e.g., ["xai"]). If set, only
            posts authored by these handles will be considered in the agentic search.
            This field cannot be set together with `excluded_x_handles`.
        excluded_x_handles: Optional list of X usernames (without the '@' symbol) used to
            exclude posts from specific accounts. If set, posts authored by these handles
            will be excluded from the agentic search results. This field cannot be set
            together with `allowed_x_handles`.
        enable_image_understanding: Enables understanding/interpreting images included in X posts.
        enable_video_understanding: Enables understanding/interpreting videos included in X posts.

    Returns:
        A `chat_pb2.Tool` object configured for X search.

    Example:
        ```
        import datetime
        from xai_sdk.tools import x_search

        # Create an X search tool for recent posts from specific users
        tool = x_search(
            from_date=datetime.datetime(2025, 1, 1),
            allowed_x_handles=["xai", "elonmusk"],
            enable_image_understanding=True,
            enable_video_understanding=True
        )
        ```
    """
    from_date_pb = Timestamp()
    to_date_pb = Timestamp()

    if from_date is not None:
        from_date_pb.FromDatetime(from_date)
    if to_date is not None:
        to_date_pb.FromDatetime(to_date)

    return chat_pb2.Tool(
        x_search=chat_pb2.XSearch(
            from_date=from_date_pb if from_date is not None else None,
            to_date=to_date_pb if to_date is not None else None,
            allowed_x_handles=allowed_x_handles,
            excluded_x_handles=excluded_x_handles,
            enable_image_understanding=enable_image_understanding,
            enable_video_understanding=enable_video_understanding,
        )
    )


def code_execution() -> chat_pb2.Tool:
    """Creates a server-side tool for code execution, typically used in agentic requests.

    This tool enables the model to execute code during conversation, allowing it to run
    computations, test algorithms, or perform data analysis as part of generating responses.

    Returns:
        A `chat_pb2.Tool` object configured for code execution.

    Example:
        ```
        from xai_sdk.tools import code_execution

        # Create a code execution tool
        tool = code_execution()
        ```
    """
    return chat_pb2.Tool(code_execution=chat_pb2.CodeExecution())


def collections_search(collection_ids: list[str], limit: Optional[int] = None) -> chat_pb2.Tool:
    """Creates a server-side tool for collections search, typically used in agentic requests.

    This tool enables the model to search collections and access document content from
    the collections during conversation.

    Args:
        collection_ids: The IDs of the collections to search in. A maximum of 10 collections can be searched.
        limit: The maximum number of results to return. Defaults to 10 if not provided.

    Returns:
        A `chat_pb2.Tool` object configured for collections search.

    Example:
        ```
        from xai_sdk.tools import collections_search

        # Create a collections search tool for the collections with the IDs "collection-1" and "collection-2"
        tool = collections_search(collection_ids=["collection-1", "collection-2"], limit=10)
        ```
    """
    return chat_pb2.Tool(
        collections_search=chat_pb2.CollectionsSearch(
            collection_ids=collection_ids,
            limit=limit,
        )
    )


def mcp(
    server_url: str,
    server_label: str | None = None,
    server_description: str | None = None,
    allowed_tool_names: list[str] | None = None,
    authorization: str | None = None,
    extra_headers: dict[str, str] | None = None,
) -> chat_pb2.Tool:
    """Creates a server-side tool for connecting to a remote MCP server, typically used in agentic requests.

    This tool enables the model to call tools on a remote MCP server

    Args:
        server_url: The URL of the MCP server.
        server_label: Optional label of the MCP server. This will be used to prefix tool names if provided.
        server_description: Optional description of the MCP server.
        server_label: The label of the MCP server. This will be used to prefix tool names if provided.
        server_description: The description of the MCP server.
        allowed_tool_names: The names of the tools that the model is allowed to call. If empty, all tools are allowed.
        authorization: The authorization token for the MCP server.
        extra_headers: The extra headers for the MCP server.
    """
    return chat_pb2.Tool(
        mcp=chat_pb2.MCP(
            server_label=server_label,
            server_description=server_description,
            server_url=server_url,
            allowed_tool_names=allowed_tool_names,
            authorization=authorization,
            extra_headers=extra_headers,
        )
    )


def get_tool_call_type(tool_call: chat_pb2.ToolCall) -> str:
    """Gets the type of a tool call.

    Args:
        tool_call: The tool call to get the type of.

    Returns:
        The type of the tool call as a string, valid values are: "client_side_tool", "web_search_tool",
        "x_search_tool", "code_execution_tool", "collections_search_tool", "mcp_tool".
    """
    return chat_pb2.ToolCallType.Name(tool_call.type).removeprefix("TOOL_CALL_TYPE_").lower()
