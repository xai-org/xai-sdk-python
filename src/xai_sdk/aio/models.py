from typing import Sequence

from google.protobuf import empty_pb2

from ..models import BaseClient
from ..proto import models_pb2


class Client(BaseClient):
    """Async Client for interacting with model metadata.

    The team is identified by the XAI_API_KEY used when instantiating the client.
    """

    async def list_language_models(self) -> Sequence[models_pb2.LanguageModel]:
        """Returns a list of all language models associated with API key used to make the request."""
        response = await self._stub.ListLanguageModels(empty_pb2.Empty())
        return response.models

    async def get_language_model(self, name: str) -> models_pb2.LanguageModel:
        """Retrieves a specific language model by name."""
        return await self._stub.GetLanguageModel(models_pb2.GetModelRequest(name=name))

    async def list_embedding_models(self) -> Sequence[models_pb2.EmbeddingModel]:
        """Returns a list of all embedding models associated with API key used to make the request."""
        response = await self._stub.ListEmbeddingModels(empty_pb2.Empty())
        return response.models

    async def get_embedding_model(self, name: str) -> models_pb2.EmbeddingModel:
        """Retrieves a specific embedding model by name."""
        return await self._stub.GetEmbeddingModel(models_pb2.GetModelRequest(name=name))

    async def list_image_generation_models(self) -> Sequence[models_pb2.ImageGenerationModel]:
        """Returns a list of all image generation models associated with API key used to make the request."""
        response = await self._stub.ListImageGenerationModels(empty_pb2.Empty())
        return response.models

    async def get_image_generation_model(self, name: str) -> models_pb2.ImageGenerationModel:
        """Retrieves a specific image generation model by name."""
        return await self._stub.GetImageGenerationModel(models_pb2.GetModelRequest(name=name))
