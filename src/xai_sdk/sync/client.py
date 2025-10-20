import os
from typing import Any, Optional, Sequence

import grpc

from ..client import BaseClient, TimeoutInterceptor, create_channel_credentials
from . import auth, chat, collections, image, models, tokenizer


class Client(BaseClient):
    """Synchronous client for connecting to the xAI API."""

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
        metadata: Optional[tuple[tuple[str, str], ...]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> None:
        """Creates the channel and sets up the sub-client."""
        api_key = api_key or os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError(
                "Trying to read the xAI API key from the XAI_API_KEY environment variable but it doesn't exist."
            )
        self._api_channel = self._make_grpc_channel(api_key, api_host, metadata, channel_options, timeout)

        # Management channel is optional, we perform further checks in the collections client
        management_api_key = management_api_key or os.getenv("XAI_MANAGEMENT_KEY")
        self._management_channel = (
            self._make_grpc_channel(management_api_key, management_api_host, metadata, channel_options, timeout)
            if management_api_key
            else None
        )

        self.auth = auth.Client(self._api_channel)
        self.chat = chat.Client(self._api_channel)
        self.collections = collections.Client(self._api_channel, self._management_channel)
        self.image = image.Client(self._api_channel)
        self.models = models.Client(self._api_channel)
        self.tokenize = tokenizer.Client(self._api_channel)

    def _make_grpc_channel(
        self,
        api_key: str,
        api_host: str,
        metadata: Optional[tuple[tuple[str, str], ...]],
        channel_options: Sequence[tuple[str, Any]],
        timeout: float,
    ) -> grpc.Channel:
        """Creates a gRPC channel with a default timeout."""
        channel = grpc.secure_channel(
            api_host,
            create_channel_credentials(api_key, api_host, metadata),
            options=channel_options,
        )
        channel = grpc.intercept_channel(channel, TimeoutInterceptor(timeout))
        return channel

    def close(self) -> None:
        """Close method to properly clean up gRPC channels."""
        if self._management_channel is not None:
            self._management_channel.close()

        if self._api_channel is not None:
            self._api_channel.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.close()
