"""Tests for xai_sdk.tools module."""

import datetime
from unittest import mock

import pytest

from xai_sdk import tools
from xai_sdk.proto import chat_pb2


class TestWebSearch:
    """Tests for web_search tool."""

    def test_basic_web_search(self):
        """Test creating a basic web search tool."""
        tool = tools.web_search()
        assert tool.HasField("web_search")
        assert tool.web_search.excluded_domains == []
        assert tool.web_search.allowed_domains == []

    def test_web_search_with_excluded_domains(self):
        """Test web search with excluded domains."""
        excluded = ["spam.com", "fake.com"]
        tool = tools.web_search(excluded_domains=excluded)
        assert tool.web_search.excluded_domains == excluded

    def test_web_search_with_allowed_domains(self):
        """Test web search with allowed domains."""
        allowed = ["github.com", "stackoverflow.com"]
        tool = tools.web_search(allowed_domains=allowed)
        assert tool.web_search.allowed_domains == allowed

    def test_web_search_with_image_options(self):
        """Test web search with image understanding and search enabled."""
        tool = tools.web_search(
            enable_image_understanding=True,
            enable_image_search=True,
        )
        assert tool.web_search.enable_image_understanding
        assert tool.web_search.enable_image_search

    def test_web_search_with_location(self):
        """Test web search with user location."""
        tool = tools.web_search(
            user_location_country="US",
            user_location_city="San Francisco",
            user_location_region="California",
            user_location_timezone="America/Los_Angeles",
        )
        assert tool.web_search.user_location.country == "US"
        assert tool.web_search.user_location.city == "San Francisco"
        assert tool.web_search.user_location.region == "California"
        assert tool.web_search.user_location.timezone == "America/Los_Angeles"


class TestXSearch:
    """Tests for x_search tool."""

    def test_basic_x_search(self):
        """Test creating a basic X search tool."""
        tool = tools.x_search()
        assert tool.HasField("x_search")

    def test_x_search_with_date_range(self):
        """Test X search with date range."""
        from_date = datetime.datetime(2025, 1, 1)
        to_date = datetime.datetime(2025, 1, 31)
        tool = tools.x_search(from_date=from_date, to_date=to_date)
        assert tool.x_search.from_date.seconds > 0
        assert tool.x_search.to_date.seconds > 0

    def test_x_search_with_handles(self):
        """Test X search with allowed X handles."""
        allowed = ["xai", "elonmusk"]
        tool = tools.x_search(allowed_x_handles=allowed)
        assert tool.x_search.allowed_x_handles == allowed

    def test_x_search_with_excluded_handles(self):
        """Test X search with excluded X handles."""
        excluded = ["spam_bot", "fake_account"]
        tool = tools.x_search(excluded_x_handles=excluded)
        assert tool.x_search.excluded_x_handles == excluded

    def test_x_search_with_media_options(self):
        """Test X search with image and video understanding."""
        tool = tools.x_search(
            enable_image_understanding=True,
            enable_video_understanding=True,
        )
        assert tool.x_search.enable_image_understanding
        assert tool.x_search.enable_video_understanding


class TestCodeExecution:
    """Tests for code_execution tool."""

    def test_code_execution(self):
        """Test creating a code execution tool."""
        tool = tools.code_execution()
        assert tool.HasField("code_execution")


class TestCollectionsSearch:
    """Tests for collections_search tool."""

    def test_basic_collections_search(self):
        """Test creating a basic collections search tool."""
        collection_ids = ["col_123", "col_456"]
        tool = tools.collections_search(collection_ids)
        assert tool.HasField("collections_search")
        assert list(tool.collections_search.collection_ids) == collection_ids

    def test_collections_search_with_limit(self):
        """Test collections search with result limit."""
        collection_ids = ["col_123"]
        tool = tools.collections_search(collection_ids, limit=10)
        assert tool.collections_search.limit == 10

    def test_collections_search_with_instructions(self):
        """Test collections search with custom instructions."""
        collection_ids = ["col_123"]
        instructions = "Find documents about machine learning"
        tool = tools.collections_search(collection_ids, instructions=instructions)
        assert tool.collections_search.instructions == instructions


class TestMCP:
    """Tests for mcp tool."""

    def test_basic_mcp(self):
        """Test creating a basic MCP tool."""
        server_url = "http://localhost:3000"
        tool = tools.mcp(server_url)
        assert tool.HasField("mcp")
        assert tool.mcp.server_url == server_url

    def test_mcp_with_label_and_description(self):
        """Test MCP tool with label and description."""
        server_url = "http://localhost:3000"
        label = "my_mcp_server"
        description = "My custom MCP server"
        tool = tools.mcp(server_url, server_label=label, server_description=description)
        assert tool.mcp.server_label == label
        assert tool.mcp.server_description == description

    def test_mcp_with_allowed_tools(self):
        """Test MCP tool with allowed tool names."""
        server_url = "http://localhost:3000"
        allowed_tools = ["tool1", "tool2", "tool3"]
        tool = tools.mcp(server_url, allowed_tool_names=allowed_tools)
        assert list(tool.mcp.allowed_tool_names) == allowed_tools

    def test_mcp_with_authorization(self):
        """Test MCP tool with authorization token."""
        server_url = "http://localhost:3000"
        auth = "Bearer token123"
        tool = tools.mcp(server_url, authorization=auth)
        assert tool.mcp.authorization == auth

    def test_mcp_with_extra_headers(self):
        """Test MCP tool with extra headers."""
        server_url = "http://localhost:3000"
        headers = {"X-Custom-Header": "value", "X-Another": "header"}
        tool = tools.mcp(server_url, extra_headers=headers)
        assert dict(tool.mcp.extra_headers) == headers


class TestGetToolCallType:
    """Tests for get_tool_call_type function."""

    def test_get_web_search_tool_type(self):
        """Test getting type of web search tool call."""
        tool_call = chat_pb2.ToolCall(type=chat_pb2.TOOL_CALL_TYPE_WEB_SEARCH)
        assert tools.get_tool_call_type(tool_call) == "web_search_tool"

    def test_get_x_search_tool_type(self):
        """Test getting type of X search tool call."""
        tool_call = chat_pb2.ToolCall(type=chat_pb2.TOOL_CALL_TYPE_X_SEARCH)
        assert tools.get_tool_call_type(tool_call) == "x_search_tool"

    def test_get_code_execution_tool_type(self):
        """Test getting type of code execution tool call."""
        tool_call = chat_pb2.ToolCall(type=chat_pb2.TOOL_CALL_TYPE_CODE_EXECUTION)
        assert tools.get_tool_call_type(tool_call) == "code_execution_tool"

    def test_get_collections_search_tool_type(self):
        """Test getting type of collections search tool call."""
        tool_call = chat_pb2.ToolCall(
            type=chat_pb2.TOOL_CALL_TYPE_COLLECTIONS_SEARCH
        )
        assert tools.get_tool_call_type(tool_call) == "collections_search_tool"

    def test_get_mcp_tool_type(self):
        """Test getting type of MCP tool call."""
        tool_call = chat_pb2.ToolCall(type=chat_pb2.TOOL_CALL_TYPE_MCP)
        assert tools.get_tool_call_type(tool_call) == "mcp_tool"
