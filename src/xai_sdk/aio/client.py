import os
from typing import Any, Optional, Sequence

import grpc

from ..client import BaseClient, UnaryStreamAioInterceptor, UnaryUnaryAioInterceptor, create_channel_credentials
from . import auth, chat, collections, image, models, tokenizer


class Client(BaseClient):
    """Asynchronous client for connecting to the xAI API."""

    auth: "auth.Client"
    chat: "chat.Client"
    collections: "collections.Client"
    image: "image.Client"
    models: "models.Client"
    tokenize: "tokenizer.Client"

    def _init(
        self,
        api_key: Optional[str],
        management_api_key: Optional[str],
        api_host: str,
        management_api_host: str,
        metadata: Optional[tuple[tuple[str, str]]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> None:
        """Creates the channel and sets up the sub-client."""
        api_key = api_key or os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Trying to read the xAI API key from the XAI_API_KEY environment variable but it doesn't exist."
            )

        api_channel = self._make_grpc_channel(api_key, api_host, metadata, channel_options, timeout)

        # Management channel is optional, we perform further checks in the collections client
        management_api_key = management_api_key or os.getenv("XAI_MANAGEMENT_KEY")
        management_channel = (
            self._make_grpc_channel(management_api_key, management_api_host, metadata, channel_options, timeout)
            if management_api_key
            else None
        )

        self.auth = auth.Client(api_channel)
        self.chat = chat.Client(api_channel)
        self.collections = collections.Client(api_channel, management_channel)
        self.image = image.Client(api_channel)
        self.models = models.Client(api_channel)
        self.tokenize = tokenizer.Client(api_channel)

    def _make_grpc_channel(
        self,
        api_key: str,
        api_host: str,
        metadata: Optional[tuple[tuple[str, str]]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> grpc.aio.Channel:
        """Creates a gRPC channel with a default timeout."""
        channel = grpc.aio.secure_channel(
            api_host,
            create_channel_credentials(api_key, api_host, metadata),
            options=channel_options,
            interceptors=[UnaryUnaryAioInterceptor(timeout), UnaryStreamAioInterceptor(timeout)],  # type: ignore
        )
        return channel
