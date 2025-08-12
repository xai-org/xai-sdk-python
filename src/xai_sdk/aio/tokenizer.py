from typing import Sequence

from opentelemetry.trace import SpanKind

from ..proto import tokenize_pb2
from ..telemetry import get_tracer
from ..tokenizer import BaseClient

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Async Client for interacting with the `Tokenize` API."""

    async def tokenize_text(self, text: str, model: str) -> Sequence[tokenize_pb2.Token]:
        """Returns the token sequence corresponding to the input text.

        Args:
            text: The text to tokenize.
            model: The model to use for tokenization.

        Returns:
            The token sequence corresponding to the input text.
        """
        with tracer.start_as_current_span(
            name=f"tokenize_text {model}",
            kind=SpanKind.CLIENT,
            attributes={"gen_ai.request.model": model},
        ):
            response = await self._stub.TokenizeText(tokenize_pb2.TokenizeTextRequest(text=text, model=model))
            return response.tokens
