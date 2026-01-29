from datetime import timedelta
from typing import Sequence, cast

from absl import app, flags

import xai_sdk
from xai_sdk.video import VideoAspectRatio, VideoResolution

MODEL = flags.DEFINE_string("model", "grok-imagine-video", "Video generation model to use.")
IMAGE_URL = flags.DEFINE_string(
    "image-url",
    "",
    "Optional input image (URL or base64 data URL) to use as the first frame (image-to-video).",
)
VIDEO_URL = flags.DEFINE_string(
    "video-url",
    "",
    "Optional input video (URL or base64 data URL) to edit based on the prompt (video-to-video).",
)
DURATION = flags.DEFINE_integer("duration", 0, "Optional duration in seconds (1-15). Use 0 to omit.")
ASPECT_RATIO = flags.DEFINE_string(
    "aspect-ratio",
    "",
    'Optional aspect ratio. One of: "1:1", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3".',
)
RESOLUTION = flags.DEFINE_string("resolution", "", 'Optional resolution. One of: "480p", "720p".')
TIMEOUT = flags.DEFINE_integer("timeout", 600, "Timeout in seconds for polling.")
INTERVAL = flags.DEFINE_integer("interval", 1, "Polling interval in seconds.")


def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.Client()

    duration = DURATION.value or None
    image_url = IMAGE_URL.value or None
    video_url = VIDEO_URL.value or None
    aspect_ratio = cast(VideoAspectRatio, ASPECT_RATIO.value) if ASPECT_RATIO.value else None
    resolution = cast(VideoResolution, RESOLUTION.value) if RESOLUTION.value else None

    previous_video_url: str | None = video_url
    first_turn = True

    while True:
        prompt = input("Prompt (blank to stop): " if first_turn else "Edit prompt (blank to stop): ")
        if not prompt:
            return

        try:
            response = client.video.generate(
                prompt=prompt,
                model=MODEL.value,
                image_url=image_url if first_turn else None,
                video_url=previous_video_url,
                duration=duration,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                timeout=timedelta(seconds=TIMEOUT.value),
                interval=timedelta(seconds=INTERVAL.value),
            )
            print(f"Respects moderation: {response.respect_moderation}")
            if response.respect_moderation:
                print(f"Video URL: {response.url}")
            else:
                print("Video URL not returned due to moderation.")
            print(f"Duration: {response.duration}s")

            # Chain edits: use the returned URL as the next input video.
            if response.respect_moderation:
                previous_video_url = response.url
                first_turn = False
        except RuntimeError as e:
            # request expired
            print(e)
        except ValueError as e:
            # unknown deferred status
            print(e)


if __name__ == "__main__":
    app.run(main)
