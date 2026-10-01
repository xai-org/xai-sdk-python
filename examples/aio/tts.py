import asyncio

from xai_sdk import AsyncClient


async def main():
    client = AsyncClient()

    voices = await client.tts.list_voices()
    print("Available voices:")
    for voice in voices.voices:
        print(f"  {voice.voice_id:10s}  {voice.name}")

    response = await client.tts.synthesize(
        "Hello from the xAI Python SDK Text to Speech API.",
        language="en",
        voice_id="eve",
    )
    response.write_to_file("hello_async.mp3")
    print(f"Saved {len(response.audio):,} bytes to hello_async.mp3 ({response.content_type})")


if __name__ == "__main__":
    asyncio.run(main())
