from datetime import timedelta
from typing import Sequence

from absl import app, flags

import xai_sdk

MODEL = flags.DEFINE_string("model", "grok-imagine-video", "Video generation model to use.")
VIDEO_URL = flags.DEFINE_string(
    "video-url",
    "",
    "Input video (URL or base64 data URL) to extend.",
)
DURATION = flags.DEFINE_integer("duration", 0, "Optional extension duration in seconds (1-10). Use 0 to omit.")
TIMEOUT = flags.DEFINE_integer("timeout", 600, "Timeout in seconds for polling.")
INTERVAL = flags.DEFINE_integer("interval", 1, "Polling interval in seconds.")


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    if not VIDEO_URL.value:
        raise app.UsageError("--video-url is required.")

    client = xai_sdk.Client()

    duration = DURATION.value or None
    video_url = VIDEO_URL.value

    while True:
        prompt = input("Extension prompt (blank to stop): ")
        if not prompt:
            return

        try:
            response = client.video.extend(
                prompt=prompt,
                model=MODEL.value,
                video_url=video_url,
                duration=duration,
                timeout=timedelta(seconds=TIMEOUT.value),
                interval=timedelta(seconds=INTERVAL.value),
            )
            print(f"Respects moderation: {response.respect_moderation}")
            if response.respect_moderation:
                print(f"Video URL: {response.url}")
            else:
                print("Video URL not returned due to moderation.")
            print(f"Duration: {response.duration}s")

            # Chain extensions: use the returned URL as the next input video.
            if response.respect_moderation:
                video_url = response.url
        except RuntimeError as e:
            # request expired
            print(e)
        except ValueError as e:
            # video URL missing from response
            print(e)


if __name__ == "__main__":
    app.run(main)
