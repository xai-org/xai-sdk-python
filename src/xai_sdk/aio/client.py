from typing import Any, Optional, Sequence

import grpc

from ..client import BaseClient, UnaryStreamAioInterceptor, UnaryUnaryAioInterceptor, create_channel_credentials
from . import auth, chat, documents, image, models, tokenizer


class Client(BaseClient):
    """Asynchronous client for connecting to the xAI API."""

    auth: "auth.Client"
    chat: "chat.Client"
    documents: "documents.Client"
    image: "image.Client"
    models: "models.Client"
    tokenize: "tokenizer.Client"

    def _init(
        self,
        api_key: Optional[str],
        api_host: str,
        metadata: Optional[tuple[tuple[str, str]]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> None:
        """Creates the channel and sets up the sub-client."""
        channel = grpc.aio.secure_channel(
            api_host,
            create_channel_credentials(api_key, api_host, metadata),
            options=channel_options,
            interceptors=[UnaryUnaryAioInterceptor(timeout), UnaryStreamAioInterceptor(timeout)],
        )

        self.auth = auth.Client(channel)
        self.chat = chat.Client(channel)
        self.documents = documents.Client(channel)
        self.image = image.Client(channel)
        self.models = models.Client(channel)
        self.tokenize = tokenizer.Client(channel)
