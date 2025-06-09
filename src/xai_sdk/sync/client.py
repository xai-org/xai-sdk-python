from typing import Any, Optional, Sequence

import grpc

from ..client import BaseClient, TimeoutInterceptor, create_channel_credentials
from . import auth, chat, image, models, tokenizer


class Client(BaseClient):
    """Synchronous client for connecting to the xAI API."""

    auth: "auth.Client"
    chat: "chat.Client"
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
        channel = grpc.secure_channel(
            api_host,
            create_channel_credentials(api_key, api_host, metadata),
            options=channel_options,
        )
        channel = grpc.intercept_channel(channel, TimeoutInterceptor(timeout))

        self.auth = auth.Client(channel)
        self.chat = chat.Client(channel)
        self.image = image.Client(channel)
        self.models = models.Client(channel)
        self.tokenize = tokenizer.Client(channel)
