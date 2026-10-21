from typing import Literal, TypeAlias, Union

from pydantic import TypeAdapter
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
    "GuidelineValidator",
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

GuidelineCategory: TypeAlias = Literal["sexual", "violence", "self_harm", "illicit", "profanity"]
GuidelineBehavior: TypeAlias = Literal["decline", "offer_support"]


class Guideline(TypedDict):
    """One output guideline, in the same shape as the REST `guidelines` entries.

    `behavior` must be one that `category` supports: `decline` for every category, and
    `offer_support` only for `self_harm`.
    """

    type: Literal["policy"]
    category: GuidelineCategory
    behavior: GuidelineBehavior


GuidelineValidator = TypeAdapter(Guideline)

GuidelineCategoryMap: dict[GuidelineCategory, "chat_pb2.GuidelineCategory"] = {
    "sexual": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_SEXUAL,
    "violence": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_VIOLENCE,
    "self_harm": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_SELF_HARM,
    "illicit": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_ILLICIT,
    "profanity": chat_pb2.GuidelineCategory.GUIDELINE_CATEGORY_PROFANITY,
}

GuidelineBehaviorMap: dict[GuidelineBehavior, "chat_pb2.GuidelineBehavior"] = {
    "decline": chat_pb2.GuidelineBehavior.GUIDELINE_BEHAVIOR_DECLINE,
    "offer_support": chat_pb2.GuidelineBehavior.GUIDELINE_BEHAVIOR_OFFER_SUPPORT,
}
