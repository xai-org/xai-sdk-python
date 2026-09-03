from typing import Any, cast

import pytest

from xai_sdk.tools import mcp


def test_mcp_rejects_plain_string_allowlist():
    with pytest.raises(TypeError, match="must be a list"):
        mcp("https://example.invalid/mcp", allowed_tool_names=cast(Any, "safe"))


def test_mcp_rejects_tuple_outside_annotated_contract():
    with pytest.raises(TypeError, match="must be a list"):
        mcp("https://example.invalid/mcp", allowed_tool_names=cast(Any, ("safe",)))


@pytest.mark.parametrize("invalid", [[1], [True], [None], ["safe", 1]])
def test_mcp_rejects_non_string_members(invalid):
    with pytest.raises(TypeError, match="contain only strings"):
        mcp("https://example.invalid/mcp", allowed_tool_names=invalid)


def test_mcp_preserves_valid_list():
    tool = mcp("https://example.invalid/mcp", allowed_tool_names=["safe", "lookup"])
    assert list(tool.mcp.allowed_tool_names) == ["safe", "lookup"]


def test_mcp_preserves_documented_empty_semantics():
    omitted = mcp("https://example.invalid/mcp", allowed_tool_names=None)
    empty = mcp("https://example.invalid/mcp", allowed_tool_names=[])
    assert omitted.SerializeToString(deterministic=True) == empty.SerializeToString(deterministic=True)
