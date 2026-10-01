from xai_sdk import Client


def main():
    client = Client()

    voices = client.tts.list_voices()
    print("Available voices:")
    for voice in voices.voices:
        print(f"  {voice.voice_id:10s}  {voice.name}")

    response = client.tts.synthesize(
        "Hello from the xAI Python SDK Text to Speech API.",
        language="en",
        voice_id="eve",
    )
    response.write_to_file("hello.mp3")
    print(f"Saved {len(response.audio):,} bytes to hello.mp3 ({response.content_type})")

    timed = client.tts.synthesize(
        "Hello world.",
        language="en",
        voice_id="eve",
        with_timestamps=True,
    )
    assert timed.audio_timestamps is not None
    print(f"Timed audio duration: {timed.duration:.2f}s")
    for char, start, end in timed.audio_timestamps.pairs()[:5]:
        print(f"  {char!r:>5}  {start:.2f}s - {end:.2f}s")


if __name__ == "__main__":
    main()
