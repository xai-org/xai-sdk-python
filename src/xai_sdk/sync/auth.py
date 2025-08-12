from google.protobuf import empty_pb2
from opentelemetry.trace import SpanKind

from ..auth import BaseClient
from ..proto import auth_pb2
from ..telemetry import get_tracer

tracer = get_tracer(__name__)


class Client(BaseClient):
    """Synchronous client for interacting with the `Auth` API."""

    def get_api_key_info(self) -> auth_pb2.ApiKey:
        """Retrieves metadata about the API key used to instantiate the client.

        Returns:
            auth_pb2.ApiKey: An object containing API key metadata, including:
            - redacted_api_key: The partially masked API key.
            - user_id: The ID of the user associated with the key.
            - name: The name of the API key.
            - create_time: When the key was created.
            - modify_time: When the key was last modified.
            - modified_by: The user ID of the user that last modified the key.
            - team_id: The ID of the team owning the key.
            - acls: Access control lists for the key.
            - api_key_id: The unique ID of the API key.
            - api_key_blocked: Whether the API key is blocked.
            - team_blocked: Whether the team is blocked.
            - disabled: Whether the API key is disabled.
        """
        with tracer.start_as_current_span(
            name="get_api_key_info",
            kind=SpanKind.CLIENT,
        ):
            return self._stub.get_api_key_info(empty_pb2.Empty())
