from typing import Sequence

from ..proto import tokenize_pb2
from ..tokenizer import BaseClient


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
        response = await self._stub.TokenizeText(tokenize_pb2.TokenizeTextRequest(text=text, model=model))
        return response.tokens
