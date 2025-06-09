from typing import Sequence

from ..proto import tokenize_pb2
from ..tokenizer import BaseClient


class Client(BaseClient):
    """Synchronous client for interacting with the `Tokenize` API."""

    def tokenize_text(self, text: str, model: str) -> Sequence[tokenize_pb2.Token]:
        """Returns the token sequence corresponding to the input text using the specified model.

        Args:
            text: The text to tokenize.
            model: The model to use for tokenization.

        Returns:
            The token sequence corresponding to the input text.
        """
        response = self._stub.TokenizeText(tokenize_pb2.TokenizeTextRequest(text=text, model=model))
        return response.tokens
