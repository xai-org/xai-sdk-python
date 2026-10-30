from typing import Literal, TypeAlias, Union

from typing_extensions import TypedDict

from ..proto import chat_pb2

__all__ = [
    "AgentCount",
    "AgentCountMap",
    "Content",
    "Guideline",
    "GuidelineBehavior",
    "GuidelineBehaviorMap",
    "GuidelineCategory",
    "GuidelineCategoryMap",
    "ImageDetail",
    "IncludeOption",
    "IncludeOptionMap",
    "ReasoningEffort",
    "ResponseFormat",
    "ToolMode",
]

AgentCount: TypeAlias = Literal[4, 16]
ReasoningEffort: TypeAlias = Literal["none", "low", "medium", "high", "xhigh"]
ImageDetail: TypeAlias = Literal["auto", "low", "high"]
Content: TypeAlias = Union[str, chat_pb2.Content]
ToolMode: TypeAlias = Literal["auto", "none", "required"]


# json_schema purposefully omitted, since the `parse` method should be used when needing json_schema responses.
ResponseFormat: TypeAlias = Literal["text", "json_object"]

IncludeOption: TypeAlias = Literal[
    "web_search_call_output",
    "x_search_call_output",
    "code_execution_call_output",
    "collections_search_call_output",
    "attachment_search_call_output",
    "mcp_call_output",
    "inline_citations",
    "verbose_streaming",
]

IncludeOptionMap: dict[IncludeOption, "chat_pb2.IncludeOption"] = {
    "web_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_WEB_SEARCH_CALL_OUTPUT,
    "x_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_X_SEARCH_CALL_OUTPUT,
    "code_execution_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_CODE_EXECUTION_CALL_OUTPUT,
    "collections_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_COLLECTIONS_SEARCH_CALL_OUTPUT,
    "attachment_search_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_ATTACHMENT_SEARCH_CALL_OUTPUT,
    "mcp_call_output": chat_pb2.IncludeOption.INCLUDE_OPTION_MCP_CALL_OUTPUT,
    "inline_citations": chat_pb2.IncludeOption.INCLUDE_OPTION_INLINE_CITATIONS,
    "verbose_streaming": chat_pb2.IncludeOption.INCLUDE_OPTION_VERBOSE_STREAMING,
}

AgentCountMap: dict[AgentCount, "chat_pb2.AgentCount"] = {
    4: chat_pb2.AgentCount.AGENT_COUNT_4,
    16: chat_pb2.AgentCount.AGENT_COUNT_16,
}

GuidelineCategory: TypeAlias = Literal["nsfw", "violence", "profanity", "cyber"]
GuidelineBehavior: TypeAlias = Literal["decline", "allow"]


class Guideline(TypedDict):
    """One output guideline, in the same shape as the REST `guidelines` entries."""

    type: Literal["policy"]
    category: GuidelineCategory
    behavior: GuidelineBehavior


GuidelineCategoryMap: dict[GuidelineCategory, "chat_pb2.GuidelineCategory"] = {
    "nsfw": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_NSFW,
    "violence": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_VIOLENCE,
    "profanity": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_PROFANITY,
    "cyber": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_CYBER,
}

GuidelineBehaviorMap: dict[GuidelineBehavior, "chat_pb2.GuidelineBehavior"] = {
    "decline": chat_pb2.GuidelineBehavior.GUIDELINE_BEHAVIOR_DECLINE,
    "allow": chat_pb2.GuidelineBehavior.GUIDELINE_BEHAVIOR_ALLOW,
}
