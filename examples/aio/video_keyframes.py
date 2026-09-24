"""Four seasons in one request: a pinned first frame, keyframes and a pinned last frame together.

Generates a winter oak with an image model, edits that still into spring, summer and autumn, then
pins all four in a single video request: winter as the exact first frame, spring and summer as
keyframes, and autumn as the exact last frame. Editing one source image keeps the tree, field and
camera angle consistent, so the video moves smoothly from pin to pin. Pinned frames require
grok-imagine-video-1.5.

Example:
  uv run examples/aio/video_keyframes.py
  uv run examples/aio/video_keyframes.py --duration 12 --resolution 480p
"""

import asyncio
from typing import Sequence, cast

from absl import app, flags

import xai_sdk
from xai_sdk.types import VideoResolution

MODEL = flags.DEFINE_string(
    "model", "grok-imagine-video-1.5", "Video model; pinned frames need grok-imagine-video-1.5."
)
IMAGE_MODEL = flags.DEFINE_string("image-model", "grok-imagine-image", "Image model used to create the stills.")
DURATION = flags.DEFINE_integer("duration", 9, "Clip length in seconds (2-15). Keyframes are spaced evenly.")
RESOLUTION = flags.DEFINE_enum(
    "resolution", "720p", ["480p", "720p"], "Video resolution. 1080p is unavailable once a frame is pinned."
)

WINTER_PROMPT = (
    "Photorealistic wide landscape: a lone oak tree on a gentle rise in the middle of a ploughed field in "
    "late winter, bare branches against an overcast sky, the tree centered, camera at eye level."
)
KEEP_SCENE = "Keep the exact same tree, field, horizon and camera angle."
SEASON_EDITS = {
    "spring": f"Spring: fresh green leaves and white blossom on the tree, green shoots in the field. {KEEP_SCENE}",
    "summer": f"High summer: a dense dark-green canopy, a golden wheat field, blue sky with cumulus. {KEEP_SCENE}",
    "autumn": f"Autumn: blazing orange and red leaves, a few drifting down, low golden-hour sun. {KEEP_SCENE}",
}
VIDEO_PROMPT = (
    "A locked-off time-lapse of a single oak across a year: buds burst into blossom, the canopy thickens "
    "through summer, then blazes orange in autumn while clouds race overhead"
)


async def main(argv: Sequence[str]) -> None:
    if len(argv) > 1:
        raise app.UsageError("Unexpected command line arguments.")

    client = xai_sdk.AsyncClient()

    winter = await client.image.sample(WINTER_PROMPT, model=IMAGE_MODEL.value, aspect_ratio="16:9", image_format="url")
    stills = {"winter": winter.url}
    edits = await asyncio.gather(
        *(
            client.image.sample(prompt, model=IMAGE_MODEL.value, image_url=stills["winter"], image_format="url")
            for prompt in SEASON_EDITS.values()
        )
    )
    stills.update({season: edited.url for season, edited in zip(SEASON_EDITS, edits, strict=True)})
    for season, url in stills.items():
        print(f"{season}: {url}")

    duration = DURATION.value
    print(f"Rendering a {duration}s clip...")
    response = await client.video.generate(
        prompt=VIDEO_PROMPT,
        model=MODEL.value,
        # Alongside keyframes or a last frame, `image_url` pins the exact first frame.
        image_url=stills["winter"],
        keyframes=[
            {"image_url": stills["spring"], "timestamp": duration / 3},
            {"image_url": stills["summer"], "timestamp": 2 * duration / 3},
        ],
        last_frame_url=stills["autumn"],
        duration=duration,
        aspect_ratio="16:9",
        resolution=cast(VideoResolution, RESOLUTION.value),
    )

    print(f"Video URL: {response.url}")
    if response.cost_usd is not None:
        print(f"Cost in USD: ${response.cost_usd:.2f}")


if __name__ == "__main__":
    app.run(lambda argv: asyncio.run(main(argv)))
