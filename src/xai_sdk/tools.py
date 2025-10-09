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
