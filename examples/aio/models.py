import asyncio
from typing import Sequence

from absl import app, flags

from xai_sdk import AsyncClient

OPERATION = flags.DEFINE_enum("operation", "list", ["list", "get"], "Operation to perform.")
MODEL_TYPE = flags.DEFINE_enum("model-type", None, ["language", "embedding", "image"], "Model type to list.")
MODEL_NAME = flags.DEFINE_string("model-name", None, "Model name to get.")


async def list_language_models(client: AsyncClient) -> None:
    """List all language models associated with the API key used to make the request."""
    language_models = await client.models.list_language_models()
    for model in language_models:
        print(f"Model name: {model.name}")
        print(f"Aliases: {model.aliases}")
        print(f"Version: {model.version}")
        print(f"Input modalities: {model.input_modalities}")
        print(f"Output modalities: {model.output_modalities}")
        print(f"Prompt text token price: {model.prompt_text_token_price}")
        print(f"Prompt image token price: {model.prompt_image_token_price}")
        print(f"Cached prompt token price: {model.cached_prompt_token_price}")
        print(f"Completion text token price: {model.completion_text_token_price}")
        print(f"Search price: {model.search_price}")
        print(f"Created: {model.created}")
        print(f"Max prompt length: {model.max_prompt_length}")
        print(f"System fingerprint: {model.system_fingerprint}")


async def list_image_generation_models(client: AsyncClient) -> None:
    """List all image generation models associated with the API key used to make the request."""
    image_models = await client.models.list_image_generation_models()
    for model in image_models:
        print(f"Model name: {model.name}")
        print(f"Aliases: {model.aliases}")
        print(f"Version: {model.version}")
        print(f"Input modalities: {model.input_modalities}")
        print(f"Output modalities: {model.output_modalities}")
        print(f"Image price: {model.image_price}")
        print(f"Created: {model.created}")
        print(f"Max prompt length: {model.max_prompt_length}")
        print(f"System fingerprint: {model.system_fingerprint}")


async def list_embedding_models(client: AsyncClient) -> None:
    """List all embedding models associated with the API key used to make the request."""
    embedding_models = await client.models.list_embedding_models()
    for model in embedding_models:
        print(f"Model name: {model.name}")
        print(f"Aliases: {model.aliases}")
        print(f"Version: {model.version}")
        print(f"Input modalities: {model.input_modalities}")
        print(f"Output modalities: {model.output_modalities}")
        print(f"Prompt text token price: {model.prompt_text_token_price}")
        print(f"Prompt image token price: {model.prompt_image_token_price}")
        print(f"Created: {model.created}")
        print(f"System fingerprint: {model.system_fingerprint}")


async def get_language_model(client: AsyncClient, model_name: str) -> None:
    """Get a specific language model by its name"""
    language_model = await client.models.get_language_model(model_name)
    print(f"Model name: {language_model.name}")
    print(f"Aliases: {language_model.aliases}")
    print(f"Version: {language_model.version}")
    print(f"Input modalities: {language_model.input_modalities}")
    print(f"Output modalities: {language_model.output_modalities}")
    print(f"Prompt text token price: {language_model.prompt_text_token_price}")
    print(f"Prompt image token price: {language_model.prompt_image_token_price}")
    print(f"Cached prompt token price: {language_model.cached_prompt_token_price}")
    print(f"Completion text token price: {language_model.completion_text_token_price}")
    print(f"Search price: {language_model.search_price}")
    print(f"Created: {language_model.created}")
    print(f"Max prompt length: {language_model.max_prompt_length}")
    print(f"System fingerprint: {language_model.system_fingerprint}")


async def get_embedding_model(client: AsyncClient, model_name: str) -> None:
    """Get a specific embedding model by its name."""
    embedding_model = await client.models.get_embedding_model(model_name)
    print(f"Model name: {embedding_model.name}")
    print(f"Aliases: {embedding_model.aliases}")
    print(f"Version: {embedding_model.version}")
    print(f"Output modalities: {embedding_model.output_modalities}")
    print(f"Prompt text token price: {embedding_model.prompt_text_token_price}")
    print(f"Prompt image token price: {embedding_model.prompt_image_token_price}")
    print(f"Created: {embedding_model.created}")
    print(f"System fingerprint: {embedding_model.system_fingerprint}")


async def get_image_generation_model(client: AsyncClient, model_name: str) -> None:
    """Get a specific image generation model by its name."""
    image_generation_model = await client.models.get_image_generation_model(model_name)
    print(f"Model name: {image_generation_model.name}")
    print(f"Aliases: {image_generation_model.aliases}")
    print(f"Version: {image_generation_model.version}")
    print(f"Output modalities: {image_generation_model.output_modalities}")
    print(f"Image price: {image_generation_model.image_price}")
    print(f"Created: {image_generation_model.created}")
    print(f"Max prompt length: {image_generation_model.max_prompt_length}")
    print(f"System fingerprint: {image_generation_model.system_fingerprint}")


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = AsyncClient()

    match (OPERATION.value, MODEL_TYPE.value, MODEL_NAME.value):
        case ("list", "language", None):
            await list_language_models(client)
        case ("list", "embedding", None):
            await list_embedding_models(client)
        case ("list", "image", None):
            await list_image_generation_models(client)
        case ("get", "language", model_name):
            await get_language_model(client, model_name)  # type: ignore
        case ("get", "embedding", model_name):
            await get_embedding_model(client, model_name)  # type: ignore
        case ("get", "image", model_name):
            await get_image_generation_model(client, model_name)  # type: ignore
        case _:
            raise app.UsageError("Unexpected command line arguments.")


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
